# application/summarization_service.py

from typing import Optional, List
from ..shared import Result, AppError, LogBus
from ..domain.chat_domain import (
    ConversationRepository,
    ChatMessageDTO,
    ConversationSummaryDTO,
    TokenCounter,
)
from ..domain.llm_domain import LLMClient, LLMRequest, ChatMessage


class SummarizationService:
    """
    Orchestrates periodic conversation summarization based on token growth.

    The service checks newly appended messages since the latest stored summary.
    If the number of tokens in the new messages exceeds a configurable threshold,
    it builds a summarization prompt and requests an LLM to generate a new summary,
    then persists it via the repository.

    Dependencies:
        - ConversationRepository: persistence for messages and summaries.
        - LLMClient: LLM adapter used to generate summaries.
        - TokenCounter: utility to compute token usage for text payloads.
        - LogBus: shared logging bus; a topic is created on initialization.
    """

    def __init__(
        self,
        repo: ConversationRepository,
        llm: LLMClient,
        counter: TokenCounter,
        log_topic: str = "app.sum",
    ):
        """
        Initialize the summarization service.

        Args:
            repo: Repository implementation for conversations and summaries.
            llm: LLM adapter used to generate summaries.
            counter: Token counting utility.
            log_topic: Log topic name for this service.
        """
        self._repo = repo
        self._llm = llm
        self._tok = counter
        self._log = LogBus.instance().topic(log_topic)

    def maybe_summarize(
        self,
        conversation_id: str,
        summarize_prompt_template: str,
        # Example: "Briefly summarize the following dialogue focusing on key facts and decisions."
        trigger_tokens_threshold: int = 3000,
        max_summary_tokens: int = 1024,
    ) -> Result[Optional[ConversationSummaryDTO], AppError]:
        """
        Conditionally summarize a conversation if new content exceeds a token threshold.

        Strategy:
            1) Fetch the latest stored summary and determine the last covered sequence.
            2) Load messages since that sequence.
            3) If the token count of new messages >= threshold, build a prompt that includes
               the previous summary (if any) plus recent messages, then call the LLM.
            4) Persist the new summary and return it.

        Args:
            conversation_id: Target conversation identifier.
            summarize_prompt_template: System-level instruction for the summarizer.
            trigger_tokens_threshold: Minimum tokens in new messages required to trigger summarization.
            max_summary_tokens: Max generation tokens for the summary.

        Returns:
            Result containing the appended ConversationSummaryDTO if a summary was created,
            `Ok(None)` if no summarization was needed, or `Err(AppError)` on failure.
        """
        latest = self._repo.latest_summary(conversation_id).unwrap_or(None)
        last_seq = self._repo.last_seq(conversation_id).unwrap_or(0)  # may be used by callers
        after_seq = latest.upto_seq if latest else 0

        new_msgs: List[ChatMessageDTO] = self._repo.list_messages_since(
            conversation_id, after_seq=after_seq, limit=2000
        ).unwrap_or([])

        if not new_msgs:
            self._log.debug("No new messages; skipping summarization.", conversation_id=conversation_id)
            return Result.Ok(None)

        # Compute tokens for new messages only.
        joined = "\n".join(f"[{m.role}] {m.content}" for m in new_msgs)
        new_tokens = self._tok.count(joined)
        if new_tokens < trigger_tokens_threshold:
            self._log.debug(
                "New tokens below threshold; skipping summarization.",
                conversation_id=conversation_id,
                new_tokens=new_tokens,
                threshold=trigger_tokens_threshold,
            )
            return Result.Ok(None)

        # Build the user payload: (previous summary if present) + (recent messages).
        pieces = []
        if latest:
            pieces.append(f"Previous summary:\n{latest.summary_text}\n")
        pieces.append("Recent messages:\n" + joined)

        # Defensive truncation to avoid oversized payloads for providers.
        user_payload = "\n".join(pieces)[:12000]

        sys_msg = ChatMessage(role="system", content=summarize_prompt_template)
        usr_msg = ChatMessage(role="user", content=user_payload)
        req = LLMRequest(messages=[sys_msg, usr_msg], temperature=0.2, max_tokens=max_summary_tokens)

        llm_res = self._llm.generate(req)
        if llm_res.is_err():
            err = llm_res.unwrap_err()
            self._log.error("LLM summarization failed.", conversation_id=conversation_id, error=str(err))
            return Result.Err(err)

        summary_text = llm_res.unwrap().text.strip()

        dto = ConversationSummaryDTO(
            id="",  # ID to be assigned by the repository/persistence layer
            conversation_id=conversation_id,
            summary_text=summary_text,
            upto_seq=max(m.seq or 0 for m in new_msgs),
            created_at=0.0,  # Timestamp to be set by the repository if applicable
            token_count=self._tok.count(summary_text),
            meta={},
        )

        self._log.info(
            "Appending new conversation summary.",
            conversation_id=conversation_id,
            upto_seq=dto.upto_seq,
            summary_tokens=dto.token_count,
        )
        return self._repo.append_summary(dto)

# application/conversation_service.py

from typing import Optional, Dict, Any, List

from ..shared import Result, AppError, LogBus
from ..domain.llm_domain import LLMClient, ChatMessage, LLMRequest
from ..domain.prompt_domain import PromptBudget
from ..domain.chat_domain import ConversationRepository, ChatMessageDTO
from .prompt_builder import PromptBuilder
from .rag_context_service import RAGContextService
from .summarization_service import SummarizationService


class ConversationService:
    """
    High-level orchestration service that coordinates the full user–assistant
    interaction cycle, including message persistence, RAG retrieval,
    prompt building, model invocation, and summarization.

    Flow:
        1. Persist the user message.
        2. Retrieve optional RAG context.
        3. Build a token-budgeted prompt.
        4. Generate an assistant reply via the LLM.
        5. Persist the assistant response.
        6. Optionally trigger summarization when message volume increases.
    """

    def __init__(
        self,
        repo: ConversationRepository,
        llm: LLMClient,
        builder: PromptBuilder,
        ragctx: RAGContextService,
        summarizer: SummarizationService,
        log_topic: str = "app.conv",
    ):
        """
        Initialize the conversation orchestrator.

        Args:
            repo: Conversation repository for message and summary persistence.
            llm: LLM adapter used for response generation.
            builder: Prompt builder responsible for assembling the LLM input.
            ragctx: RAG context service for retrieving external context.
            summarizer: Summarization service to maintain conversation summaries.
            log_topic: LogBus topic name for this service.
        """
        self._repo = repo
        self._llm = llm
        self._builder = builder
        self._rag = ragctx
        self._sum = summarizer
        self._log = LogBus.instance().topic(log_topic)

    def handle_user_message(
        self,
        conversation_id: str,
        user_text: str,
        instruction_prompt_template: str,
        summarize_prompt_template: str,
        budget: PromptBudget,
        rag_k: int = 5,
    ) -> Result[str, AppError]:
        """
        Handle a single user message and produce the assistant's response.

        The process persists the user message, optionally enriches it with
        RAG context, builds a prompt within token constraints, invokes the LLM,
        stores the response, and optionally triggers summarization.

        Args:
            conversation_id: Unique conversation identifier.
            user_text: Raw user message content.
            instruction_prompt_template: Template for the system instruction.
                Must contain `{user_text}` placeholder.
            summarize_prompt_template: Template used for generating conversation summaries.
            budget: PromptBudget specifying context and token constraints.
            rag_k: Number of top documents to retrieve for RAG context.

        Returns:
            Result containing the assistant reply text or an AppError.
        """
        # 0) Persist user message
        self._repo.insert_message(
            ChatMessageDTO(
                id="",
                conversation_id=conversation_id,
                role="user",
                content=user_text,
                created_at=0.0,
            )
        )

        # 1) Retrieve optional RAG context
        ctx = self._rag.fetch_context(
            user_text, k=rag_k, budget=budget.max_context_tokens
        ).unwrap_or("")

        # 2) Build prompt
        instruction_prompt = instruction_prompt_template.format(user_text=user_text)
        built = self._builder.build(conversation_id, instruction_prompt, ctx, budget)
        if built.is_err():
            err = built.unwrap_err()
            self._log.error(
                "Prompt building failed.",
                conversation_id=conversation_id,
                error=str(err),
            )
            return Result.Err(err)

        bp = built.unwrap()

        # 3) Construct message sequence for the LLM
        msgs: List[ChatMessage] = [ChatMessage(role="system", content=bp.instruction_prompt)]

        if bp.context_block:
            msgs.append(ChatMessage(role="system", content=f"Context:\n{bp.context_block}"))
        if bp.summary_block:
            msgs.append(ChatMessage(role="system", content=f"Summary:\n{bp.summary_block}"))

        msgs.extend([ChatMessage(**m) for m in bp.history_messages])
        msgs.append(ChatMessage(role="user", content=user_text))

        # 4) Generate assistant reply
        res = self._llm.generate(LLMRequest(messages=msgs, temperature=0.2))
        if res.is_err():
            err = res.unwrap_err()
            self._log.error(
                "LLM generation failed.",
                conversation_id=conversation_id,
                error=str(err),
            )
            return Result.Err(err)

        answer = res.unwrap().text.strip()

        # 5) Persist assistant response
        self._repo.insert_message(
            ChatMessageDTO(
                id="",
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
                created_at=0.0,
            )
        )

        # 6) Trigger summarization (synchronous for simplicity)
        self._sum.maybe_summarize(
            conversation_id=conversation_id,
            summarize_prompt_template=summarize_prompt_template,
        )

        self._log.info(
            "User message handled successfully.",
            conversation_id=conversation_id,
            tokens_budget=budget.context_window,
            has_context=bool(ctx),
            answer_preview=answer[:120],
        )

        return Result.Ok(answer)

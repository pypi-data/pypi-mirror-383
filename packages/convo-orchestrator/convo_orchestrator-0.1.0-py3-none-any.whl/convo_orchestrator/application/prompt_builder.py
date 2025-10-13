# application/prompt_builder.py

from typing import Dict, List, Optional

from ..shared import Result, AppError, LogBus
from ..domain.prompt_domain import PromptBudget, BuiltPrompt
from ..domain.chat_domain import ConversationRepository, TokenCounter


"""
Prompt assembly service.

Builds a prompt within a fixed token budget by combining:
  1) Instruction block (required).
  2) Optional RAG context (if present and within budget).
  3) Optional latest conversation summary (if present and within budget).
  4) Recent conversation history (added newest-to-oldest until budget is reached).

All token accounting relies on the provided TokenCounter.
"""


class PromptBuilder:
    """
    Constructs a prompt for model inference while respecting a token budget.
    """

    def __init__(self, repo: ConversationRepository, counter: TokenCounter, log_topic: str = "app.prompt"):
        """
        Args:
            repo: Conversation repository used to fetch summaries and recent messages.
            counter: Token counting utility for text and message lists.
            log_topic: LogBus topic name for builder diagnostics.
        """
        self._repo = repo
        self._tok = counter
        self._log = LogBus.instance().topic(log_topic)

    def build(
        self,
        conversation_id: str,
        instruction_prompt: str,
        rag_context: Optional[str],
        budget: PromptBudget,
    ) -> Result[BuiltPrompt, AppError]:
        """
        Assemble a `BuiltPrompt` that fits within the provided `PromptBudget`.

        Strategy:
            - Always include the instruction block.
            - Include RAG context if it fits within the context allowance.
            - Include the latest summary if it fits within the summary allowance.
            - Fill remaining budget with the most recent messages (newest first),
              stopping before exceeding the budget.

        Args:
            conversation_id: Target conversation id.
            instruction_prompt: Core instruction block (must include the current user message).
            rag_context: Optional RAG context text; may be omitted or empty.
            budget: Token budget configuration.

        Returns:
            Result containing a `BuiltPrompt` with token counts filled in.
        """
        total = 0

        # 1) Instruction block (required)
        instr_tokens = self._tok.count(instruction_prompt)
        total += instr_tokens

        # 2) RAG context (optional; limited by max_context_tokens)
        context_block: Optional[str] = None
        if rag_context:
            ctx_tokens = self._tok.count(rag_context)
            if total + ctx_tokens <= instr_tokens + budget.max_context_tokens:
                context_block = rag_context
                total += ctx_tokens

        # 3) Latest summary (optional; limited by max_summary_tokens)
        summary_block: Optional[str] = None
        latest_sum = self._repo.latest_summary(conversation_id).unwrap_or(None)
        if latest_sum:
            sum_tokens = latest_sum.token_count or self._tok.count(latest_sum.summary_text)
            # Instruction + (allowed context) + summary <= instr + max_context + max_summary
            if total + sum_tokens <= instr_tokens + budget.max_context_tokens + budget.max_summary_tokens:
                summary_block = latest_sum.summary_text
                total += sum_tokens

        # 4) Recent history (fill up to max_history_tokens, without exceeding window - reserve)
        hist: List[Dict[str, str]] = []
        remaining = budget.context_window - budget.reserve_margin - total
        remaining = min(remaining, budget.max_history_tokens)

        if remaining > 0:
            recent = self._repo.list_recent_messages(conversation_id, limit=200).unwrap_or([])
            # Add messages from newest to oldest, but prepend to keep chronological order
            recent_sorted = sorted(recent, key=lambda m: (m.seq or 0))
            for m in reversed(recent_sorted):
                msg = {"role": m.role, "content": m.content}
                t = m.token_count or self._tok.count_messages([msg])
                if t <= remaining:
                    hist.insert(0, msg)  # Prepend older messages at the front as we walk backwards
                    remaining -= t
                else:
                    break

            total = budget.context_window - budget.reserve_margin - remaining

        built = BuiltPrompt(
            instruction_prompt=instruction_prompt,
            summary_block=summary_block,
            history_messages=hist,
            context_block=context_block,
            total_tokens=total,
        )

        self._log.debug(
            "Prompt built.",
            conversation_id=conversation_id,
            total_tokens=total,
            instr_tokens=instr_tokens,
            has_context=bool(context_block),
            has_summary=bool(summary_block),
            history_messages=len(hist),
        )

        return Result.Ok(built)

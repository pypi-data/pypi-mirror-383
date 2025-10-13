# domain/prompt_domain.py

from dataclasses import dataclass
from typing import Dict, List, Optional


"""
Prompt-related domain definitions.

This module defines the core data structures used to represent prompt assembly
and token budgeting for LLM interactions. It focuses on describing how much
context can fit into a model’s context window and what components are included
in the final prompt.
"""


@dataclass
class PromptBudget:
    """
    Token budget configuration for prompt construction.

    Attributes:
        context_window: Total model context window in tokens (e.g., 8192, 32768).
        reserve_margin: Number of tokens reserved to avoid overflow.
        max_context_tokens: Token limit available for RAG context (if used).
        max_summary_tokens: Token limit for including a conversation summary.
        max_history_tokens: Remaining tokens available for recent messages.
    """
    context_window: int
    reserve_margin: int
    max_context_tokens: int
    max_summary_tokens: int
    max_history_tokens: int


@dataclass
class BuiltPrompt:
    """
    Represents the fully constructed prompt ready for model inference.

    Attributes:
        instruction_prompt: Core system or instruction block (required).
        summary_block: Optional conversation summary block, if present and within budget.
        history_messages: List of message dicts forming recent conversation history.
        context_block: Optional retrieved context block, if included.
        total_tokens: Total token count for all concatenated prompt parts.
    """
    instruction_prompt: str
    summary_block: Optional[str]
    history_messages: List[Dict[str, str]]
    context_block: Optional[str]
    total_tokens: int

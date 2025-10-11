"""Memory-aware routing for context-sensitive agent selection."""

from __future__ import annotations

from typing import Any, Callable

from kagura.core.memory import MemoryManager

from .context_analyzer import ContextAnalyzer
from .router import AgentRouter


class MemoryAwareRouter(AgentRouter):
    """Router that considers conversation history for better routing.

    Extends AgentRouter with memory-aware capabilities:
    - Detects context-dependent queries (pronouns, implicit references)
    - Retrieves relevant context from conversation history
    - Enhances queries with context before routing
    - Supports semantic context retrieval via RAG

    Example:
        >>> from kagura import agent
        >>> from kagura.core.memory import MemoryManager
        >>> from kagura.routing import MemoryAwareRouter
        >>>
        >>> memory = MemoryManager(agent_name="assistant", enable_rag=True)
        >>> router = MemoryAwareRouter(
        ...     memory=memory,
        ...     context_window=5,
        ...     use_semantic_context=True
        ... )
        >>>
        >>> @agent
        >>> async def translator(text: str, target_lang: str) -> str:
        ...     '''Translate {{ text }} to {{ target_lang }}'''
        >>>
        >>> router.register(translator, intents=["translate", "翻訳"])
        >>>
        >>> # First query
        >>> await router.route("Translate 'hello' to French")
        >>> # Second query (context-dependent)
        >>> await router.route("What about Spanish?")
        >>> # Router understands "Spanish" refers to translation
    """

    def __init__(
        self,
        memory: MemoryManager,
        strategy: str = "intent",
        fallback_agent: Callable | None = None,
        confidence_threshold: float = 0.3,
        encoder: str = "openai",
        context_window: int = 5,
        use_semantic_context: bool = True,
    ) -> None:
        """Initialize memory-aware router.

        Args:
            memory: MemoryManager instance for accessing conversation history
            strategy: Routing strategy ("intent" or "semantic")
            fallback_agent: Default agent when no match found
            confidence_threshold: Minimum confidence score (0.0-1.0)
            encoder: Encoder for semantic routing
            context_window: Number of recent messages to consider
            use_semantic_context: Whether to use RAG for semantic context retrieval
        """
        super().__init__(
            strategy=strategy,
            fallback_agent=fallback_agent,
            confidence_threshold=confidence_threshold,
            encoder=encoder,
        )

        self.memory = memory
        self.context_window = context_window
        self.use_semantic_context = use_semantic_context
        self.context_analyzer = ContextAnalyzer()

    async def route(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Route user input with memory awareness.

        Args:
            user_input: User's natural language input
            context: Optional context information
            **kwargs: Additional arguments to pass to the selected agent

        Returns:
            Result from executing the selected agent

        Raises:
            NoAgentFoundError: When no suitable agent is found
        """
        # Check if query needs context
        needs_context = self.context_analyzer.needs_context(user_input)

        # Enhance query with context if needed
        enhanced_input = user_input
        if needs_context:
            enhanced_input = await self._enhance_with_context(user_input)

        # Store the user message in memory for future context
        self.memory.add_message("user", user_input)

        # Route with enhanced input
        try:
            result = await super().route(enhanced_input, context, **kwargs)

            # Store the result as assistant message
            if result is not None:
                result_str = str(result)
                self.memory.add_message("assistant", result_str)

            return result
        except Exception as e:
            # Store error in memory
            self.memory.add_message("assistant", f"Error: {str(e)}")
            raise

    async def _enhance_with_context(self, query: str) -> str:
        """Enhance query with conversation context.

        Args:
            query: Original user query

        Returns:
            Enhanced query with context
        """
        # Get recent conversation history
        recent_messages = self.memory.get_llm_context(last_n=self.context_window)

        # Use context analyzer to extract intent
        enhanced = self.context_analyzer.extract_intent_from_context(
            query, recent_messages
        )

        # If RAG is enabled, add semantic context
        if self.use_semantic_context and self.memory.rag:
            try:
                semantic_results = self.memory.recall_semantic(query, top_k=3)

                if semantic_results:
                    # Add relevant semantic context
                    semantic_context = "\n".join(
                        result["content"] for result in semantic_results[:2]
                    )
                    enhanced = f"{enhanced}\n\nRelevant context:\n{semantic_context}"
            except ValueError:
                # RAG not enabled, skip semantic context
                pass

        return enhanced

    def get_conversation_summary(self, last_n: int = 10) -> str:
        """Get a summary of recent conversation.

        Args:
            last_n: Number of recent messages to include

        Returns:
            Formatted conversation summary
        """
        messages = self.memory.get_context(last_n=last_n)

        if not messages:
            return "No conversation history"

        summary_lines = []
        for msg in messages:
            role = msg.role.title()
            content = (
                msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            )
            summary_lines.append(f"{role}: {content}")

        return "\n".join(summary_lines)

    def clear_context(self) -> None:
        """Clear conversation context from memory."""
        self.memory.context.clear()

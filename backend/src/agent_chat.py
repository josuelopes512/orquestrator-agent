"""
Integration with Claude Agent SDK for chat functionality.
This module handles the communication with Claude AI using the Agent SDK.
"""
from typing import AsyncGenerator
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


class ClaudeAgentChat:
    """Handler for Claude Agent SDK integration"""

    def __init__(self):
        """Initialize the Claude Agent Chat handler"""
        # No need for API key - Agent SDK uses Claude Code authentication
        pass

    async def _stream_response_gemini(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from Gemini using the GeminiAgent.

        Args:
            messages: List of conversation messages
            model: Gemini model to use (e.g., "gemini-1.5-pro")
            system_prompt: Optional system prompt

        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            from .gemini_agent import GeminiAgent

            # Get current working directory from active project
            from .database import async_session_maker
            from .models.project import ActiveProject
            from sqlalchemy import select

            cwd = Path.cwd()
            async with async_session_maker() as session:
                result = await session.execute(
                    select(ActiveProject).order_by(ActiveProject.loaded_at.desc()).limit(1)
                )
                active_project = result.scalar_one_or_none()
                if active_project:
                    cwd = Path(active_project.path)

            # Initialize Gemini agent
            gemini = GeminiAgent(model=model)

            # Stream response
            async for chunk in gemini.chat_completion(messages, system_prompt):
                yield chunk

        except Exception as e:
            error_msg = f"Error in Gemini Agent: {str(e)}"
            print(f"[ClaudeAgentChat] {error_msg}")
            raise RuntimeError(error_msg)

    async def stream_response(
        self,
        messages: list[dict],
        model: str = "claude-3.5-sonnet",
        system_prompt: str | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from Claude Agent SDK or Gemini using the /question command.

        Args:
            messages: List of conversation messages in format [{"role": "user/assistant", "content": "..."}]
            model: AI model to use (e.g., "claude-3-sonnet", "claude-3-opus", "gemini-1.5-pro")
            system_prompt: Optional system prompt (not used with /question, but kept for compatibility)

        Yields:
            str: Chunks of the response text as they arrive
        """
        # Check if it's a Gemini model
        if model.startswith("gemini"):
            async for chunk in self._stream_response_gemini(messages, model, system_prompt):
                yield chunk
            return

        try:
            # Get the last user message (the current question)
            user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break

            if not user_message:
                raise ValueError("No user message found in conversation")

            # Build context from previous messages (optional, for multi-turn conversations)
            context = ""
            if len(messages) > 1:
                context = "\n\nPrevious conversation:\n"
                for msg in messages[:-1]:  # All messages except the last one
                    role = "User" if msg["role"] == "user" else "Assistant"
                    context += f"{role}: {msg['content']}\n"

            # Execute /question command with the user's question
            prompt = f"/question {user_message}"

            # Add context if available
            if context:
                prompt += context

            # Get current working directory from active project in database
            from .database import async_session_maker
            from .models.project import ActiveProject
            from sqlalchemy import select

            cwd = Path.cwd()
            async with async_session_maker() as session:
                result = await session.execute(
                    select(ActiveProject).order_by(ActiveProject.loaded_at.desc()).limit(1)
                )
                active_project = result.scalar_one_or_none()
                if active_project:
                    cwd = Path(active_project.path)

            # Map model IDs to agent SDK model names
            model_mapping = {
                "claude-3.5-opus": "opus",
                "claude-3.5-sonnet": "sonnet",
                "claude-3.5-haiku": "haiku",
                # Keep compatibility with old model names
                "claude-3-sonnet": "sonnet",
                "claude-3-opus": "opus",
            }
            agent_model = model_mapping.get(model, "sonnet")

            # Configure agent options for chat
            options = ClaudeAgentOptions(
                cwd=cwd,
                setting_sources=["user", "project"],  # Load commands from .claude/commands/
                allowed_tools=["Read", "Bash", "Glob", "Grep", "Skill"],
                permission_mode="bypassPermissions",  # Auto-approve read operations
                model=agent_model,  # Use selected model
            )

            # Stream response from Claude Agent SDK
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    # Handle assistant messages with content blocks
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Yield text chunks
                            yield block.text

                elif isinstance(message, ResultMessage):
                    # Final result message
                    if hasattr(message, "result") and message.result:
                        yield message.result

        except Exception as e:
            error_msg = f"Error in Claude Agent SDK: {str(e)}"
            print(f"[ClaudeAgentChat] {error_msg}")
            raise RuntimeError(error_msg)

    async def get_single_response(
        self,
        messages: list[dict],
        model: str = "claude-3.5-sonnet",
        system_prompt: str | None = None
    ) -> str:
        """
        Get a complete response from Claude (non-streaming).

        Args:
            messages: List of conversation messages
            model: AI model to use
            system_prompt: Optional system prompt

        Returns:
            str: The complete response text
        """
        try:
            full_response = ""
            async for chunk in self.stream_response(messages, model, system_prompt):
                full_response += chunk
            return full_response

        except Exception as e:
            error_msg = f"Error in Claude Agent SDK: {str(e)}"
            print(f"[ClaudeAgentChat] {error_msg}")
            raise RuntimeError(error_msg)


# Default system prompt for the chat assistant (kept for reference, not used with /question)
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant integrated into a Kanban board application.
You can help users with:
- Understanding and managing their tasks
- Planning and organizing their workflow
- Answering questions about software development
- Providing coding assistance and best practices
- General questions and conversations

Be concise, friendly, and helpful. When discussing code, provide clear examples.
Keep responses focused and actionable."""


# Singleton instance
_claude_agent_instance = None


def get_claude_agent() -> ClaudeAgentChat:
    """Get or create the Claude Agent instance"""
    global _claude_agent_instance
    if _claude_agent_instance is None:
        _claude_agent_instance = ClaudeAgentChat()
    return _claude_agent_instance

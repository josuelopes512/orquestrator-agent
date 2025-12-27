from datetime import datetime
from pathlib import Path
from typing import Optional

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)

from .execution import (
    ExecutionLog,
    ExecutionRecord,
    ExecutionStatus,
    LogType,
    PlanResult,
)

# Store executions in memory
executions: dict[str, ExecutionRecord] = {}


def get_execution(card_id: str) -> Optional[ExecutionRecord]:
    """Get execution record by card ID."""
    return executions.get(card_id)


def get_all_executions() -> list[ExecutionRecord]:
    """Get all execution records."""
    return list(executions.values())


def add_log(record: ExecutionRecord, log_type: LogType, content: str) -> None:
    """Add a log entry to the execution record."""
    log = ExecutionLog(
        timestamp=datetime.now().isoformat(),
        type=log_type,
        content=content,
    )
    record.logs.append(log)
    print(f"[Agent] [{log_type.value.upper()}] {content}")


async def execute_plan(
    card_id: str,
    title: str,
    description: str,
    cwd: str,
) -> PlanResult:
    """Execute a plan using Claude Agent SDK."""
    prompt = f"/plan {title}: {description}"

    # Initialize execution record
    record = ExecutionRecord(
        cardId=card_id,
        startedAt=datetime.now().isoformat(),
        status=ExecutionStatus.RUNNING,
        logs=[],
    )
    executions[card_id] = record

    add_log(record, LogType.INFO, f"Starting plan execution for: {title}")
    add_log(record, LogType.INFO, f"Working directory: {cwd}")
    add_log(record, LogType.INFO, f"Prompt: {prompt}")

    result_text = ""

    try:
        # Configure agent options
        options = ClaudeAgentOptions(
            cwd=Path(cwd),
            setting_sources=["user", "project"],  # Load Skills from .claude/skills/
            allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep", "TodoWrite"],
            permission_mode="acceptEdits",
        )

        # Execute using claude-agent-sdk
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                # Handle assistant messages with content blocks
                for block in message.content:
                    if isinstance(block, TextBlock):
                        add_log(record, LogType.TEXT, block.text)
                        result_text += block.text + "\n"
                    elif isinstance(block, ToolUseBlock):
                        add_log(record, LogType.TOOL, f"Using tool: {block.name}")

            elif isinstance(message, ResultMessage):
                if hasattr(message, "result") and message.result:
                    result_text = message.result
                    add_log(record, LogType.RESULT, message.result)

        # Mark as success
        record.completed_at = datetime.now().isoformat()
        record.status = ExecutionStatus.SUCCESS
        record.result = result_text
        add_log(record, LogType.INFO, "Plan execution completed successfully")

        return PlanResult(
            success=True,
            result=result_text,
            logs=record.logs,
        )

    except Exception as e:
        error_message = str(e)
        record.completed_at = datetime.now().isoformat()
        record.status = ExecutionStatus.ERROR
        record.result = error_message
        add_log(record, LogType.ERROR, f"Execution error: {error_message}")

        return PlanResult(
            success=False,
            error=error_message,
            logs=record.logs,
        )

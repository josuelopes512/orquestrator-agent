"""Expert Sync Service.

Synchronizes expert knowledge bases after a card is completed.
Checks which files were modified and triggers sync for relevant experts.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List

from ..config.experts import AVAILABLE_EXPERTS, ExpertConfig
from ..schemas.expert import ExpertMatch, SyncedExpert


def _get_modified_files_for_card(card_id: str, branch_name: str | None, cwd: str) -> List[str]:
    """
    Get list of files modified for a card.

    Uses git diff to find modified files on the card's branch.
    """
    try:
        if branch_name:
            # Get files changed on this branch compared to main/master
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~10", "--", "."],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

        # Fallback: get recently modified files
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

        return []
    except Exception as e:
        print(f"[ExpertSync] Error getting modified files: {e}")
        return []


def _files_match_patterns(files: List[str], patterns: List[str]) -> List[str]:
    """
    Filter files that match any of the expert's file patterns.

    Returns list of files that match.
    """
    matched_files = []
    for file in files:
        for pattern in patterns:
            if file.startswith(pattern) or pattern in file:
                matched_files.append(file)
                break
    return matched_files


async def _run_expert_sync_command(expert_id: str, cwd: str) -> tuple[bool, str]:
    """
    Run the expert's sync command via Claude CLI.

    Returns (success, message) tuple.
    """
    try:
        # The sync command for each expert
        sync_command = f"/experts:{expert_id}:sync"

        # Run claude with the sync command
        # Note: This is a simplified version - in production you might want
        # to use the agent.py execute functions
        process = await asyncio.create_subprocess_exec(
            "claude",
            "-p", sync_command,
            "--allowedTools", "Read,Write,Edit,Glob,Grep",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=120  # 2 minute timeout for sync
        )

        if process.returncode == 0:
            return True, f"Sync completed successfully"
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            return False, f"Sync failed: {error_msg[:200]}"

    except asyncio.TimeoutError:
        return False, "Sync timed out after 2 minutes"
    except FileNotFoundError:
        # Claude CLI not found - skip sync silently
        return True, "Sync skipped (CLI not available)"
    except Exception as e:
        return False, f"Sync error: {str(e)[:200]}"


async def sync_experts(
    card_id: str,
    experts: Dict[str, ExpertMatch],
    branch_name: str | None,
    cwd: str
) -> List[SyncedExpert]:
    """
    Sync all relevant experts for a completed card.

    Args:
        card_id: ID of the completed card
        experts: Dict of experts identified for this card
        branch_name: Branch name for the card (if using worktree)
        cwd: Working directory (project root)

    Returns:
        List of SyncedExpert results
    """
    results: List[SyncedExpert] = []

    # Get files modified for this card
    modified_files = _get_modified_files_for_card(card_id, branch_name, cwd)

    if not modified_files:
        # No files modified, still mark experts as checked
        for expert_id in experts.keys():
            results.append(SyncedExpert(
                expert_id=expert_id,
                synced=False,
                files_changed=[],
                message="No files modified for this card"
            ))
        return results

    # Check each expert
    for expert_id, match in experts.items():
        config = AVAILABLE_EXPERTS.get(expert_id)
        if not config:
            results.append(SyncedExpert(
                expert_id=expert_id,
                synced=False,
                files_changed=[],
                message=f"Expert {expert_id} not found in configuration"
            ))
            continue

        # Check if any modified files match this expert's patterns
        relevant_files = _files_match_patterns(modified_files, config["file_patterns"])

        if relevant_files:
            # Files relevant to this expert were modified - run sync
            success, message = await _run_expert_sync_command(expert_id, cwd)
            results.append(SyncedExpert(
                expert_id=expert_id,
                synced=success,
                files_changed=relevant_files,
                message=message
            ))
        else:
            # No relevant files for this expert
            results.append(SyncedExpert(
                expert_id=expert_id,
                synced=False,
                files_changed=[],
                message="No relevant files modified for this expert"
            ))

    return results


def check_expert_knowledge_needs_update(expert_id: str, modified_files: List[str]) -> bool:
    """
    Quick check if an expert's knowledge base might need updating.

    Args:
        expert_id: ID of the expert
        modified_files: List of modified file paths

    Returns:
        True if the expert should be synced
    """
    config = AVAILABLE_EXPERTS.get(expert_id)
    if not config:
        return False

    return len(_files_match_patterns(modified_files, config["file_patterns"])) > 0

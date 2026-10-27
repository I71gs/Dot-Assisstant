"""
modules/automation.py — DOT Automation Module

Handles shell command execution with DANGEROUS permission gating.
"""

from __future__ import annotations

import subprocess

from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from core.permissions import PermissionLevel

log = get_logger("automation")


def run_command(command: str, **_) -> str:
    """Execute a raw shell command and return its output."""
    if not command.strip():
        return "✗ No command provided."

    log.info("run_command: %s", command)
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()

        parts: list[str] = []
        if out:
            parts.append(out)
        if err:
            parts.append(f"[stderr] {err}")
        if not parts:
            code = result.returncode
            return f"✓ Command exited with code {code}." if code == 0 else f"✗ Command failed (code {code})."
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return "✗ Command timed out after 30 seconds."
    except Exception as exc:
        log.exception("run_command failed")
        return f"✗ Error running command: {exc}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command(
            "run_command",
            run_command,
            "Run a raw shell/cmd command",
            aliases=["cmd", "exec", "run command"],
            args_help="<command>",
            category="Automation",
            permission=PermissionLevel.DANGEROUS,
        ),
    ])

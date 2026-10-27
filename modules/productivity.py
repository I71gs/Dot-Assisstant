"""
modules/productivity.py — DOT Productivity Module

Handles:
- Command history (save / show)
- Quick notes (add / read)
- To-do list (add / list / complete / remove)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import config as cfg
from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from core.permissions import PermissionLevel

log = get_logger("productivity")

# ── paths ──────────────────────────────────────────────────────────────────────
HISTORY_FILE: Path = cfg.DATA_DIR / "command_history.json"
NOTES_FILE: Path = cfg.DATA_DIR / "notes.txt"
TODO_FILE: Path = cfg.DATA_DIR / "todos.json"


# ══════════════════════════════════════════════════════════════════════════════
# Command History
# ══════════════════════════════════════════════════════════════════════════════

def _load_history() -> list[dict[str, str]]:
    if HISTORY_FILE.exists():
        try:
            with HISTORY_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_history(history: list[dict[str, str]]) -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    max_hist = cfg.get("max_history", 200)
    history = history[-max_hist:]
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def save_command_history(command: str) -> None:
    """Append a command string to persistent history."""
    history = _load_history()
    history.append({"command": command, "time": datetime.now().isoformat()})
    _save_history(history)


def show_history(count: str = "", **_) -> str:
    history = _load_history()
    if not history:
        return "No command history yet."
    n = int(count) if count and count.isdigit() else 20
    recent = history[-n:]
    lines = [f"  {i + 1:>3}. [{h['time'][:19]}] {h['command']}"
             for i, h in enumerate(recent)]
    return f"Last {len(recent)} commands:\n" + "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Notes
# ══════════════════════════════════════════════════════════════════════════════

def _ensure_notes_file() -> Path:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("", encoding="utf-8")
    return NOTES_FILE


def create_note(text: str, **_) -> str:
    path = _ensure_notes_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {text}\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(entry)
    return f"✓ Note saved: {text}"


def create_note_prompt(**_) -> str:
    try:
        text = input("  Enter your note: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "✗ Note cancelled."
    if not text:
        return "✗ Note is empty."
    return create_note(text)


def read_notes(count: str = "", **_) -> str:
    path = _ensure_notes_file()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return "No notes found."
    n = int(count) if count and count.isdigit() else 10
    shown = lines[-n:]
    return f"Last {len(shown)} notes:\n" + "\n".join(f"  {ln}" for ln in shown)


# ══════════════════════════════════════════════════════════════════════════════
# To-Do List
# ══════════════════════════════════════════════════════════════════════════════

def _load_todos() -> list[dict[str, Any]]:
    if TODO_FILE.exists():
        try:
            with TODO_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_todos(todos: list[dict[str, Any]]) -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with TODO_FILE.open("w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def add_todo(task: str, **_) -> str:
    todos = _load_todos()
    todos.append({"task": task, "done": False, "created": datetime.now().isoformat()})
    _save_todos(todos)
    return f"✓ Added task: {task}"


def add_todo_prompt(**_) -> str:
    try:
        task = input("  Task description: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "✗ Cancelled."
    if not task:
        return "✗ Task is empty."
    return add_todo(task)


def list_todos(**_) -> str:
    todos = _load_todos()
    pending = [t for t in todos if not t["done"]]
    done = [t for t in todos if t["done"]]
    if not todos:
        return "Your to-do list is empty."
    lines = []
    if pending:
        lines.append(f"Pending ({len(pending)}):")
        for i, t in enumerate(pending, 1):
            lines.append(f"  {i}. ☐ {t['task']}")
    if done:
        lines.append(f"Done ({len(done)}):")
        for i, t in enumerate(done, 1):
            lines.append(f"  {i}. ☑ {t['task']}")
    return "\n".join(lines)


def complete_todo(index: str, **_) -> str:
    try:
        idx = int(index) - 1
    except ValueError:
        return f"✗ Invalid index: {index}"
    todos = _load_todos()
    pending = [t for t in todos if not t["done"]]
    if idx < 0 or idx >= len(pending):
        return f"✗ No pending task #{index}."
    pending[idx]["done"] = True
    _save_todos(todos)
    return f"✓ Completed: {pending[idx]['task']}"


def remove_todo(index: str, **_) -> str:
    try:
        idx = int(index) - 1
    except ValueError:
        return f"✗ Invalid index: {index}"
    todos = _load_todos()
    pending = [t for t in todos if not t["done"]]
    if idx < 0 or idx >= len(pending):
        return f"✗ No pending task #{index}."
    task = pending[idx]["task"]
    todos = [t for t in todos if not (t["task"] == task and not t["done"])]
    _save_todos(todos)
    return f"✓ Removed task: {task}"


# ══════════════════════════════════════════════════════════════════════════════
# Registration
# ══════════════════════════════════════════════════════════════════════════════

def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("show_history", show_history, "Show command history",
                     aliases=["history", "command history"],
                     args_help="[count]", category="Productivity"),
        make_command("create_note", create_note, "Save a quick note",
                     aliases=["note", "take note", "add note"],
                     args_help="<text>", category="Productivity"),
        make_command("create_note_prompt", create_note_prompt, "Save a note (interactive)",
                     category="Productivity"),
        make_command("read_notes", read_notes, "Read recent notes",
                     aliases=["read notes", "show notes", "my notes"],
                     args_help="[count]", category="Productivity"),
        make_command("add_todo", add_todo, "Add a to-do task",
                     aliases=["add task", "new task"],
                     args_help="<task>", category="Productivity"),
        make_command("add_todo_prompt", add_todo_prompt, "Add a to-do task (interactive)",
                     category="Productivity"),
        make_command("list_todos", list_todos, "List all to-do items",
                     aliases=["list tasks", "show tasks", "my tasks", "todos"],
                     category="Productivity"),
        make_command("complete_todo", complete_todo, "Mark a task as done",
                     aliases=["done task", "finish task", "complete task"],
                     args_help="<index>", category="Productivity"),
        make_command("remove_todo", remove_todo, "Delete a pending task",
                     aliases=["delete task", "remove task"],
                     args_help="<index>", category="Productivity",
                     permission=PermissionLevel.CONFIRM),
    ])

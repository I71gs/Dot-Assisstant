"""
tests/test_parser.py — Unit tests for Parser
"""

from __future__ import annotations

import pytest
from core.parser import Parser


def test_basic_intents():
    parser = Parser()

    p = parser.parse("what is the time")
    assert p.intent == "get_time"

    p = parser.parse("date")
    assert p.intent == "get_date"

    p = parser.parse("exit")
    assert p.intent == "exit"


def test_command_with_arguments():
    parser = Parser()

    p = parser.parse("create file note.txt")
    assert p.intent == "create_file"
    assert p.arguments == {"filename": "note.txt"}

    p = parser.parse("rename file old.txt to new.txt")
    assert p.intent == "rename_file"
    assert p.arguments == {"source": "old.txt", "destination": "new.txt"}

    p = parser.parse("open chrome")
    assert p.intent == "open_app"
    assert p.arguments == {"app": "chrome"}


def test_reminders_parsing():
    parser = Parser()

    p = parser.parse("remind me buy groceries in 10 minutes")
    assert p.intent == "add_reminder"
    assert p.arguments == {"message": "buy groceries", "delay": "10", "unit": "minutes"}


def test_unknown_commands():
    parser = Parser()

    p = parser.parse("random gibberish that does not match rules")
    assert p.intent == "unknown"
    assert p.arguments == {}


def test_productivity_parsing():
    parser = Parser()

    p = parser.parse("note remember to buy milk")
    assert p.intent == "create_note"
    assert p.arguments == {"text": "remember to buy milk"}

    p = parser.parse("read notes 5")
    assert p.intent == "read_notes"
    assert p.arguments == {"count": "5"}

    p = parser.parse("add todo write report")
    assert p.intent == "add_todo"
    assert p.arguments == {"task": "write report"}

    p = parser.parse("list todos")
    assert p.intent == "list_todos"

    p = parser.parse("done todo 1")
    assert p.intent == "complete_todo"
    assert p.arguments == {"index": "1"}

    p = parser.parse("history 10")
    assert p.intent == "show_history"
    assert p.arguments == {"count": "10"}


def test_information_parsing():
    parser = Parser()

    p = parser.parse("weather London")
    assert p.intent == "get_weather"
    assert p.arguments == {"city": "london"}

    p = parser.parse("define serendipity")
    assert p.intent == "define_word"
    assert p.arguments == {"word": "serendipity"}

    p = parser.parse("calculate 25 * 4 + 10")
    assert p.intent == "calculate"
    assert p.arguments == {"expression": "25 * 4 + 10"}

    p = parser.parse("convert 5 km to miles")
    assert p.intent == "convert_units"
    assert p.arguments == {"value": "5", "from_unit": "km", "to_unit": "miles"}

    p = parser.parse("trivia")
    assert p.intent == "tell_trivia"

    p = parser.parse("tell me a joke")
    assert p.intent == "tell_joke"


def test_automation_parsing():
    parser = Parser()

    p = parser.parse("cmd dir /w")
    assert p.intent == "run_command"
    assert p.arguments == {"command": "dir /w"}

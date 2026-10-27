from __future__ import annotations

from core.assistant import Assistant


def test_speak_requires_confirmation(monkeypatch):
    assistant = Assistant()
    assistant._tts_enabled = True
    spoke = []

    class FakeEngine:
        def say(self, text: str) -> None:
            spoke.append(text)

        def runAndWait(self) -> None:
            return None

    assistant._tts_engine = FakeEngine()
    prompts = []

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        return "y"

    monkeypatch.setattr("builtins.input", fake_input)

    assistant._speak("hello there")

    assert prompts == ["Read this aloud? [y/N]: "]
    assert spoke == ["hello there"]

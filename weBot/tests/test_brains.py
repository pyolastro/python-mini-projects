import os
import pytest

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="Groq key not configured")
def test_groq_brain(monkeypatch):
    os.environ["BRAIN"] = "groq"
    from app import make_brain
    brain = make_brain()
    reply = brain.reply([], "Hello Groq!")
    assert isinstance(reply, str)
    assert len(reply) > 0

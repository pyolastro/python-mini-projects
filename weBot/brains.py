# brains.py
import os, time, json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterable, Optional

Message = Dict[str, Any] # {"role": "user"|"bot", "text": "...", "ts": float}

class Brain(ABC):
    @abstractmethod
    def reply(self, history: List[Message], user_input: str) -> str: ...
    # Optional: streaming interface.
    def stream_reply(self, history: List[Message], user_input: str) -> Iterable[str]:
        yield self.reply(history, user_input)

# Simple fallback brain (kept for local tests)
class RulesBrain(Brain):
    def reply(self, history, user_input):
        msg = user_input.strip().lower()
        if "hello" in msg or "hi" in msg: return "Hey! How can I help today?"
        if "time" in msg: return f"It's {time.strftime('%H:%M:%S')} on the server."
        if msg == "reset": return "Conversation reset. What’s next?"
        return f"You said: “{user_input}”. (This is the rules fallback brain.)"

# Groq (cloud)
# Docs: https://console.groq.com
class GroqBrain(Brain):
    def __init__(self, model: Optional[str] = None, timeout: int = 60):
        from groq import Groq
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set.")
        self.client = Groq(api_key=key, timeout=timeout)
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        # can be tweak defaults via env:
        # MODEL_TEMP (float), MODEL_TOP_P (float), MODEL_MAX_TOKENS (int)
        self.temp = float(os.getenv("MODEL_TEMP", "0.7"))
        self.top_p = float(os.getenv("MODEL_TOP_P", "0.95"))
        self.max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "512"))

    def _to_messages(self, history: List[Message], user_input: str):
        msgs = []
        # prepend a system prompt via env
        sys_prompt = os.getenv("SYSTEM_PROMPT", "").strip()
        if sys_prompt:
            msgs.append({"role": "system", "content": sys_prompt})
        for m in history:
            role = "assistant" if m["role"] == "bot" else "user"
            msgs.append({"role": role, "content": m["text"]})
        return msgs

    def reply(self, history: List[Message], user_input: str) -> str:
        try:
            msgs = self._to_messages(history, user_input)
            res = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                temperature=self.temp,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
            )
            return (res.choices[0].message.content or "").strip()
        except Exception as e:
            return f"(Groq error: {type(e).__name__}) Please try again."


    # Token streaming for WebSocket
    def stream_reply(self, history: List[Message], user_input: str) -> Iterable[str]:
        msgs = self._to_messages(history, user_input)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=self.temp,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

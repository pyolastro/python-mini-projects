# weBot — FastAPI + Groq AI Chatbot

A full-stack **AI chat bot** built with **Python FastAPI** and powered by **Groq’s Llama 3.1** language model.
weBot provides both **REST** and **WebSocket** APIs plus a minimal front-end for real-time chat.

## Features

* **FastAPI backend** — clean, async REST & WebSocket endpoints
* **Pluggable “Brain” architecture** - swap between rule-based, Groq, or other LLM providers
* **Groq LLM integration** - free, high-speed inference using `llama-3.1-8b-instant`
* **Live streaming chat** - WebSocket endpoint streams tokens like ChatGPT
* **Optional API-key auth** for secure use
* **Simple HTML UI** served automatically at `http://127.0.0.1:8000`

## Tech Stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Backend  | Python 3.10 +, FastAPI, Uvicorn  |
| Frontend | HTML + JavaScript (no framework) |
| LLM      | Groq Cloud API (Llama 3.1)       |
| Config   | `.env` + python-dotenv           |
| Testing  | pytest                           |
| CI/CD    | GitHub Actions                   |

## Installation

```bash
git clone https://github.com/pyolastro/python-mini-projects/weBot.git
cd weBot
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create a **`.env`** file in the project root:

```env
BRAIN=groq
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
MODEL_TEMP=0.7
MODEL_TOP_P=0.9
MODEL_MAX_TOKENS=512
ALLOW_ORIGINS=*
SYSTEM_PROMPT=You are a concise, helpful assistant.
```

> Get your free Groq API key at [https://console.groq.com](https://console.groq.com).

## Run the Bot

```bash
uvicorn app:app --reload
```

Then open your browser: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

You’ll see the minimal chat UI served automatically from the `/public` directory.
Try sending messages via:

* **REST mode:** sends one full reply per request
* **WebSocket mode:** streams tokens live as they’re generated

## API Endpoints

| Method | Endpoint             | Description                      |
| ------ | -------------------- | -------------------------------- |
| `POST` | `/chat`              | Send a message (REST)            |
| `GET`  | `/history/{user_id}` | Retrieve recent conversation     |
| `WS`   | `/ws/{user_id}`      | Persistent WebSocket chat stream |

Example REST call:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","message":"hello"}'
```


## Running Tests

```bash
pytest -v
```

## Project Structure

```
weBot/
├─ app.py # FastAPI app (REST + WebSocket)
├─ brains.py # Modular “Brain” classes (RulesBrain, GroqBrain, etc.)
├─ public/
│  └─ index.html # Frontend UI served at /
├─ tests/
│  └─ test_app.py  # pytest suite
└─ requirements.txt
```

*“weBot” demonstrates how modern LLMs can be integrated into lightweight Python microservices for both REST and real-time streaming interactions.*

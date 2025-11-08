# Voice Agent

A lightweight, modular voice assistant built in Python - designed for local use and extendable via service APIs
(Wolfram|Alpha, OpenWeather, Spotify, Wikipedia, and more).

## Features

* **Voice interaction** (speech recognition + text-to-speech)
* **Command parsing** for:

  * `okay say <message>` → speak a phrase
  * `okay wikipedia <topic>` → summarize topic
  * `okay compute <query>` → Wolfram|Alpha calculation (fallback: Wikipedia)
  * `okay weather <city>` → fetch current weather
  * `okay play <song>` → play song on Spotify
  * `okay notes <text>` → save a text note
  * `okay help` → list available commands
  * `okay exit` → quit the assistant
* Modular, testable structure
* API keys and credentials loaded from a config file

## Project Structure

```
voice_agent/
├── pyproject.toml
├── README.md
├── conf/
│   └── config.json # API keys, secrets, settings
├── src/
│   ├── main.py # Entry point
│   └── assistant/
│       ├── __init__.py
│       ├── commands.py # Command parsing and routing
│       ├── services.py # External integrations (Spotify, weather, Wolfram)
│       └── speech.py # Speech recognition and TTS
└── tests/
    ├── conftest.py
    ├── test_commands.py
    ├── test_services_spotify.py
    ├── test_services_weather.py
    └── test_services_wolfram.py
```

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/python-mini-projects/voiceAgent.git
cd voice-agent
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/bin/activate # On Linux/macOS
env\Scripts\activate # On Windows
```

### 3. Install dependencies

```bash
pip install -e .
pip install -r requirements.txt
```
*(If you use `pyproject.toml`, editable install is enough — the tests and imports will work.)*

## Configuration

API keys are read from `conf/config.ini` or environment variables.

Example `conf/config.ini`:

```ini
[KEYS]
WOLFRAM_APP_ID = your-wolfram-app-id,
OPENWEATHER_API_KEY = your-openweather-api-key,
SPOTIFY_CLIENT_ID = your-spotify-client-id,
SPOTIFY_CLIENT_SECRET = your-spotify-client-secret,
SPOTIFY_REDIRECT_URI = http://localhost:8888/callback,
SPOTIFY_SCOPE = user-modify-playback-state user-read-playback-state
```

## Run the Assistant

From the project root:

```bash
python -m src.main
```

You should hear:

> “All systems nominal.”

Then start speaking:

> “Okay say hello world”
> “Okay weather Barcelona”
> “Okay compute life universe everything”


## Running Tests

All tests are written in **pytest**.
To run them:

```bash
pytest -v
```

They include mocks for TTS and API services, so no network or audio output is needed.

Example test output:

```
==================== 13 passed in 1.8s ====================
```


## Tech Stack

* **Python 3.10+**
* **pytest** for testing
* **Requests** / **Spotipy** / **WolframAlpha API**
* **SpeechRecognition** (for parsing voice input)
* **pyttsx3** or similar (for text-to-speech output)


## Extending Commands

To add a new command:

1. Open `src/assistant/commands.py`
2. Add a new `elif cmd == "yourcommand":` block.
3. Implement behavior or delegate to a new helper in `assistant/services.py`.

Example:

```python
elif cmd == "joke":
    result = services.tell_joke()
    speak(result)
```

## 📜 License

MIT License © 2025 pyolastro

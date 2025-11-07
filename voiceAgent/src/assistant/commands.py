# src/assistant/commands.py
import logging
from datetime import datetime
from assistant.speech import speak
from assistant import services

log = logging.getLogger(__name__)
ACTIVATION = "okay"

HELP_TEXT = f"""
Available commands (prefix with '{ACTIVATION}'):
- say <words>        → Speak back your words
- wikipedia <topic>  → Summary from Wikipedia
- compute <query>    → Wolfram|Alpha compute (fallback Wikipedia)
- play <song/artist> → Play on Spotify
- weather <city>     → Current weather
- notes <text>       → Save a note to file
- help               → List commands
- exit               → Quit the assistant
"""

def handle_command(words: list[str], config: dict, sp=None):
    if not words:
        return

    if words[0] == ACTIVATION:
        words = words[1:]

    if not words:
        speak("Please say a command.")
        return

    cmd = words[0]
    rest = " ".join(words[1:]).strip()

    if cmd == "say":
        speak(rest or "Hello.")

    elif cmd == "wikipedia":
        speak(services.search_wikipedia(rest))

    elif cmd in ("compute", "computer"):
        result = services.search_wolframalpha(rest, config["WOLFRAM_APP_ID"])
        speak(result)

    elif cmd == "play":
        result = services.search_and_play_spotify(sp, rest)
        speak(result)

    elif cmd == "weather":
        result = services.search_openweather(rest, config["OPENWEATHER_API_KEY"])
        speak(result)

    elif cmd == "notes":
        speak("Ready to record your note.")
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        with open(f"note_{now}.txt", "w") as f:
            f.write(rest)
        speak("Note written.")

    elif cmd == "help":
        print(HELP_TEXT.strip())
        speak("I printed the list of available commands.")

    elif cmd == "exit":
        speak("Goodbye.")
        raise SystemExit

    else:
        speak("Unknown command.")
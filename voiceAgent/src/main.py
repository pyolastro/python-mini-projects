# src/main.py
import logging
import os
import configparser

from assistant.speech import parse_command, speak
from assistant.commands import handle_command
from assistant import services

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

def load_config():
    # Find the path to the conf_file
    base_dir = os.path.dirname(os.path.dirname(__file__))
    conf_path = os.path.join(base_dir, "conf", "conf.ini")

    config = configparser.ConfigParser()
    config.read(conf_path)
    cfg = config["KEYS"]

    return {
        "WOLFRAM_APP_ID": cfg.get("WOLFRAM_APP_ID", ""),
        "OPENWEATHER_API_KEY": cfg.get("OPENWEATHER_API_KEY", ""),
        "SPOTIFY_CLIENT_ID": cfg.get("SPOTIFY_CLIENT_ID", ""),
        "SPOTIFY_CLIENT_SECRET": cfg.get("SPOTIFY_CLIENT_SECRET", ""),
        "SPOTIFY_REDIRECT_URI": cfg.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
        "SPOTIFY_SCOPE": cfg.get("SPOTIFY_SCOPE", "user-modify-playback-state user-read-playback-state"),
    }

def main():
    config = load_config()

    sp = services.get_spotify(
        config["SPOTIFY_CLIENT_ID"],
        config["SPOTIFY_CLIENT_SECRET"],
        config["SPOTIFY_REDIRECT_URI"],
        config["SPOTIFY_SCOPE"],
    )

    speak("All systems nominal.")

    while True:
        query = parse_command()
        if not query:
            continue
        words = query.lower().split()
        try:
            handle_command(words, config, sp=sp)
        except SystemExit:
            break
        except Exception:
            log.exception("Error in command handler")
            speak("Something went wrong.")

if __name__ == "__main__":
    main()

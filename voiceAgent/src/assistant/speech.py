# src/assistant/speech.py
import logging
import pyttsx3
import speech_recognition as sr

log = logging.getLogger(__name__)

# Init speech engine
engine = pyttsx3.init()
try:
    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)  # female
except Exception:
    log.warning("Could not set preferred voice.")


def speak(text: str, rate: int = 150):
    try:
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        log.exception("TTS failed")
        print(text)


def parse_command(timeout=30, phrase_time_limit=10) -> str | None:
    recognizer = sr.Recognizer()
    log.info("Listening for a command...")
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            log.warning("Mic timeout: no speech detected")
            speak("I didn't hear anything.")
            return None

    try:
        query = recognizer.recognize_google(audio, language="en-US")
        log.info("Heard: %s", query)
        return query
    except sr.UnknownValueError:
        speak("I did not catch that.")
    except sr.RequestError as e:
        speak("Speech recognition service is unavailable.")
        log.error("Speech service error: %s", e)
    except Exception:
        log.exception("Speech recognition failed")
        speak("Something went wrong while listening.")
    return None

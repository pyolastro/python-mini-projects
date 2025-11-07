import builtins
import pytest
from unittest.mock import patch, MagicMock

from assistant.commands import handle_command

# Stub out speak() to avoid TTS during tests
@patch("assistant.commands.speak")
def test_say_command(speak, config):
    handle_command(["okay", "say", "hello", "world"], config, sp=None)
    speak.assert_called_with("hello world")

@patch("assistant.commands.speak")
@patch("assistant.services.search_wikipedia")
def test_wikipedia_command(search_wikipedia, speak, config):
    search_wikipedia.return_value = "Ada Lovelace summary"
    handle_command(["okay", "wikipedia", "Ada", "Lovelace"], config, sp=None)
    speak.assert_called_with("Ada Lovelace summary")

@patch("assistant.commands.speak")
@patch("assistant.services.search_wolframalpha")
def test_compute_command(search_wolframalpha, speak, config):
    search_wolframalpha.return_value = "42"
    handle_command(["okay", "compute", "life", "universe", "everything"], config, sp=None)
    speak.assert_called_with("42")

@patch("assistant.commands.speak")
@patch("assistant.services.search_openweather")
def test_weather_command(search_openweather, speak, config):
    search_openweather.return_value = "Clear sky, about 23°C."
    handle_command(["okay", "weather", "Barcelona"], config, sp=None)
    speak.assert_called_with("Clear sky, about 23°C.")

@patch("assistant.commands.speak")
def test_unknown_command(speak, config):
    handle_command(["okay", "bananas"], config, sp=None)
    speak.assert_called_with("Unknown command.")

@patch("assistant.commands.speak")
def test_exit_command(speak, config):
    with pytest.raises(SystemExit):
        handle_command(["okay", "exit"], config, sp=None)
    speak.assert_called_with("Goodbye.")

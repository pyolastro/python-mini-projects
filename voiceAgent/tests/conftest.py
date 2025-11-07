# tests/conftest.py
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

@pytest.fixture
def config():
    return {
        "WOLFRAM_APP_ID": "test-appid",
        "OPENWEATHER_API_KEY": "test-weather-key",
        "SPOTIFY_CLIENT_ID": "cid",
        "SPOTIFY_CLIENT_SECRET": "csec",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback",
        "SPOTIFY_SCOPE": "user-modify-playback-state user-read-playback-state",
    }

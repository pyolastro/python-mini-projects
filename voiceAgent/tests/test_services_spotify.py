from unittest.mock import MagicMock
from assistant.services import search_and_play_spotify

def test_spotify_happy_path():
    sp = MagicMock()
    sp.search.return_value = {
        "tracks": {
            "items": [
                {
                    "uri": "spotify:track:123",
                    "name": "TrackName",
                    "artists": [{"name": "ArtistName"}],
                }
            ]
        }
    }
    out = search_and_play_spotify(sp, "TrackName")
    sp.start_playback.assert_called_once_with(uris=["spotify:track:123"])
    assert "Now playing: TrackName by ArtistName." == out

def test_spotify_no_results():
    sp = MagicMock()
    sp.search.return_value = {"tracks": {"items": []}}
    out = search_and_play_spotify(sp, "NothingHere")
    assert out == "No track found."

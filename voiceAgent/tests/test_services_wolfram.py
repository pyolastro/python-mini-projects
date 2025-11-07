from unittest.mock import patch, MagicMock
from assistant.services import search_wolframalpha

@patch("assistant.services.requests.get")
@patch("assistant.services.speak")  # used on fallback
def test_wolfram_success(speak, mock_get):
    # Mock a successful JSON response with a primary pod
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "queryresult": {
            "success": True,
            "pods": [
                {"title": "Input interpretation", "subpods": [{"plaintext": "2+2"}]},
                {"title": "Result", "primary": True, "subpods": [{"plaintext": "4"}]},
            ],
        }
    }
    mock_get.return_value = mock_resp

    out = search_wolframalpha("2+2", appid="appid")
    assert out.strip() == "4"

@patch("assistant.services.requests.get")
@patch("assistant.services.speak")
def test_wolfram_fallback_to_wikipedia(speak, mock_get, monkeypatch):
    # success=False triggers Wikipedia fallback
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"queryresult": {"success": False}}
    mock_get.return_value = mock_resp

    # Mock Wikipedia summary
    from assistant import services
    monkeypatch.setattr(services, "search_wikipedia", lambda q: "Wiki fallback")

    out = search_wolframalpha("garbage", appid="appid")
    assert out == "Wiki fallback"
    speak.assert_called_once()  # “Computation failed…” feedback

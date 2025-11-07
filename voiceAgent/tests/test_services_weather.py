from unittest.mock import patch, MagicMock
from assistant.services import search_openweather

@patch("assistant.services.requests.get")
def test_weather_happy_path(mock_get):
    # First call: geocoding
    geo_resp = MagicMock()
    geo_resp.raise_for_status.return_value = None
    geo_resp.json.return_value = [{"lat": 41.3888, "lon": 2.159}]

    # Second call: current weather
    wx_resp = MagicMock()
    wx_resp.raise_for_status.return_value = None
    wx_resp.json.return_value = {
        "main": {"temp": 22.6},
        "weather": [{"description": "clear sky"}],
    }

    mock_get.side_effect = [geo_resp, wx_resp]

    out = search_openweather("Barcelona", api_key="key")
    assert "22" in out or "23" in out  # rounded temp
    assert "Clear sky" in out

@patch("assistant.services.requests.get")
def test_weather_city_not_found(mock_get):
    geo_resp = MagicMock()
    geo_resp.raise_for_status.return_value = None
    geo_resp.json.return_value = []  # not found
    mock_get.return_value = geo_resp

    out = search_openweather("Atlantis", api_key="key")
    assert "Could not find 'Atlantis'." in out

# src/assistant/services.py
import logging
import requests
import wikipedia
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from assistant.speech import speak

log = logging.getLogger(__name__)
HTTP_TIMEOUT = 10

# Wikipedia
def search_wikipedia(query: str) -> str:
    try:
        results = wikipedia.search(query)
        if not results:
            return "No Wikipedia results."
        page = wikipedia.page(results[0])
        return wikipedia.summary(page.title, sentences=3)
    except Exception as e:
        log.exception("Wikipedia failed")
        return f"Wikipedia lookup failed: {e}"


# Wolfram Alpha (JSON API)
def search_wolframalpha(query: str, appid: str) -> str:
    if not appid:
        return "Wolfram|Alpha is not configured."
    try:
        url = "https://api.wolframalpha.com/v2/query"
        params = {"appid": appid, "input": query, "output": "JSON", "format": "plaintext"}
        r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        q = data.get("queryresult", {})
        if not q.get("success"):
            speak("Computation failed. Querying universal databank.")
            return search_wikipedia(query)

        for pod in q.get("pods", []):
            if pod.get("primary") or "result" in pod.get("title", "").lower():
                return pod["subpods"][0].get("plaintext", "").split("(")[0]
        return search_wikipedia(query)
    except Exception as e:
        log.exception("Wolfram error")
        return f"Wolfram error: {e}"


# Spotify 
def get_spotify(client_id, client_secret, redirect_uri, scope):
    try:
        auth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            open_browser=True,
            cache_path=".spotipyoauthcache",
        )
        return spotipy.Spotify(auth_manager=auth)
    except Exception:
        log.exception("Spotify init failed")
        return None

def _ensure_active_device(sp, preferred_name: str | None = None) -> str | None:
    """
    Returns an active device_id if possible. If none is active but devices exist,
    transfer playback to one and return its id. Returns None if no devices are available.
    """
    try:
        devices = sp.devices().get("devices", [])
        if not devices:
            return None

        # Try preferred device by name
        if preferred_name:
            for d in devices:
                if d.get("name", "").lower() == preferred_name.lower():
                    if not d.get("is_active"):
                        sp.transfer_playback(d["id"], force_play=True)
                    return d["id"]

        # Any active device check
        for d in devices:
            if d.get("is_active"):
                return d["id"]

        # No active device: pick the first and force transfer
        target = devices[0]
        sp.transfer_playback(target["id"], force_play=True)
        return target["id"]
    except Exception:
        log.exception("Failed to ensure active device")
        return None

def search_and_play_spotify(sp, query: str, preferred_device_name: str | None = None) -> str:
    if not sp:
        return "Spotify not configured."

    try:
        results = sp.search(q=query, limit=1, type="track")
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return "No track found."

        track = tracks[0]

        if preferred_device_name:
            # Only resolve/pass device_id if caller asked for a specific device
            device_id = _ensure_active_device(sp, preferred_device_name)
            if not device_id:
                return ("No Spotify device is available. Open the Spotify app on any device (phone/desktop/web), make sure you're logged in, then try again.")
            sp.start_playback(device_id=device_id, uris=[track["uri"]])
        else:
            # Let Spotify use whatever active device is available
            sp.start_playback(uris=[track["uri"]])

        artist = track["artists"][0]["name"]
        return f"Now playing: {track['name']} by {artist}."
    except SpotifyException as e:
        # Handle the specific NO_ACTIVE_DEVICE case defensively
        if e.http_status == 404 and "NO_ACTIVE_DEVICE" in str(e).upper():
            return ("No active device found. Open Spotify on a device and try again (you can also set a preferred device name).")
        log.exception("Spotify error")
        return "Spotify playback failed."
    except Exception:
        log.exception("Spotify error")
        return "Spotify playback failed."
    
# OpenWeather
def search_openweather(city: str, api_key: str) -> str:
    if not api_key:
        return "OpenWeather is not configured."
    try:
        geo = "http://api.openweathermap.org/geo/1.0/direct"
        g = requests.get(geo, params={"q": city, "limit": 1, "appid": api_key}, timeout=HTTP_TIMEOUT)
        g.raise_for_status()
        data = g.json()
        if not data:
            return f"Could not find '{city}'."
        lat, lon = data[0]["lat"], data[0]["lon"]

        wx = "https://api.openweathermap.org/data/2.5/weather"
        w = requests.get(wx, params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}, timeout=HTTP_TIMEOUT)
        w.raise_for_status()
        d = w.json()
        temp = d["main"].get("temp")
        desc = d["weather"][0].get("description", "").capitalize()
        return f"The weather in {city}: {desc}, about {round(temp)}°C."
    except Exception as e:
        log.exception("Weather error")
        return f"Weather error: {e}"

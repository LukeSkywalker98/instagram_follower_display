# app.py
import os
import time
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# Load environment variables (expects a .env file in the same directory)
# ----------------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("IG_TOKEN")          # Long‑lived Instagram Basic Display token
if not TOKEN:
    raise RuntimeError("IG_TOKEN not found in .env – please add it.")

# ----------------------------------------------------------------------
# Flask app and simple in‑memory cache (5‑minute TTL)
# ----------------------------------------------------------------------
app = Flask(__name__)
CACHE_TTL = 300                        # seconds (5 min)
_cache = {"ts": 0, "value": None}

# ----------------------------------------------------------------------
# Helper: fetch follower count from Instagram Basic Display API
# ----------------------------------------------------------------------
def fetch_followers():
    """
    Calls:
        https://graph.instagram.com/me?fields=followers_count&access_token=TOKEN
    Returns the integer follower count.
    Raises requests.HTTPError on non‑200 responses.
    """
    url = "https://graph.instagram.com/me"
    params = {
        "fields": "followers_count",
        "access_token": TOKEN,
    }
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()                     # will raise for 4xx/5xx
    data = resp.json()
    # Expected shape: {"followers_count": 12345, "id": "..."}
    if "followers_count" not in data:
        raise ValueError("Unexpected API response: missing followers_count")
    return int(data["followers_count"])

# ----------------------------------------------------------------------
# Route: /followers – returns JSON { "followers": <int> }
# ----------------------------------------------------------------------
@app.route("/followers")
def followers():
    now = time.time()
    # Refresh cache only when TTL expired or we have no data yet
    if now - _cache["ts"] > CACHE_TTL or _cache["value"] is None:
        try:
            _cache["value"] = fetch_followers()
            _cache["ts"] = now
        except Exception as exc:
            # Log to stdout (visible in `journalctl` or `docker logs`)
            print(f"[ERROR] Failed to fetch followers: {exc}")
            return jsonify(error=str(exc)), 502
    return jsonify(followers=_cache["value"])

# ----------------------------------------------------------------------
# Development entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Debug mode is convenient locally; disable for production.
    app.run(host="0.0.0.0", port=5000, debug=True)
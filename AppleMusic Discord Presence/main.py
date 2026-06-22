import asyncio
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional
 
try:
    from pypresence import Presence
    from pypresence.types import ActivityType, StatusDisplayType
    from pypresence.exceptions import PyPresenceException
except ImportError:
    sys.exit(
        "Missing dependency 'pypresence' (or it's out of date).\n"
        "Install/upgrade it with:  pip install -U pypresence"
    )
 
try:
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
    )
    from winsdk.windows.storage.streams import Buffer, InputStreamOptions
except ImportError:
    sys.exit(
        "Missing dependency 'winsdk' (Windows-only).\n"
        "Install it with:  pip install winsdk"
    )
 
try:
    import requests
except ImportError:
    sys.exit(
        "Missing dependency 'requests'.\n"
        "Install it with:  pip install requests"
    )
 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
 
DEFAULT_CONFIG = {
    "discord_client_id": "YOUR_DISCORD_APPLICATION_ID",
    "app_id_match": "applemusic",
    "show_profile_button": False,
    "profile_button_label": "Show Apple Music Profile",
    "profile_url": "",
    "poll_interval_seconds": 5,
}
 
ARTIST_JUNK_SEPARATORS = (" — ", " – ", " -- ", " - ", " | ", " • ", " · ")
 
 
def clean_artist(raw_artist: str, album: str) -> str:
    artist = (raw_artist or "").strip()
    if not artist:
        return artist
 
    for sep in ARTIST_JUNK_SEPARATORS:
        if sep in artist:
            artist = artist.split(sep, 1)[0].strip()
            break
 
    album = (album or "").strip()
    if album and artist.lower() != album.lower() and artist.lower().endswith(album.lower()):
        artist = artist[: -len(album)].strip(" -–—|•·,")
 
    return artist.strip()
 
 
@dataclass
class TrackInfo:
    name: str
    artist: str
    album: str
    duration: float
    position: float
    thumbnail_bytes: Optional[bytes] = None
 
 
def load_config() -> dict:
    needs_regen = not os.path.exists(CONFIG_PATH)
 
    user_cfg = {}
    if not needs_regen:
        with open(CONFIG_PATH) as f:
            raw = f.read()
        if not raw.strip():
            needs_regen = True
        else:
            try:
                user_cfg = json.loads(raw)
            except json.JSONDecodeError as e:
                sys.exit(
                    f"{CONFIG_PATH} contains invalid JSON ({e}).\n"
                    f"Fix it, or delete the file and re-run this script to "
                    f"regenerate a clean default config."
                )
 
    if needs_regen:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"No usable config found, created a fresh one at:\n  {CONFIG_PATH}")
        print("Open it, set 'discord_client_id', then run this again.")
        sys.exit(1)
 
    return {**DEFAULT_CONFIG, **user_cfg}
 
 
MAX_THUMBNAIL_BYTES = 5 * 1024 * 1024  # max buffer limit dokunma
 
 
async def read_thumbnail_bytes(thumbnail_ref) -> Optional[bytes]:
    if thumbnail_ref is None:
        return None
    try:
        stream = await thumbnail_ref.open_read_async()
        size = stream.size
        if size <= 0 or size > MAX_THUMBNAIL_BYTES:
            return None
        buf = Buffer(size)
        await stream.read_async(buf, size, InputStreamOptions.READ_AHEAD)
        return bytes(buf)
    except Exception:
        return None
 
 
async def get_now_playing(app_id_match: str) -> Optional[TrackInfo]:
    try:
        manager = await MediaManager.request_async()
    except Exception:
        return None
 
    target_session = None
    for session in manager.get_sessions():
        aumid = (session.source_app_user_model_id or "").lower()
        if app_id_match.lower() in aumid:
            target_session = session
            break
 
    if target_session is None:
        return None
 
    playback_info = target_session.get_playback_info()
    if playback_info.playback_status != PlaybackStatus.PLAYING:
        return None
 
    try:
        props = await target_session.try_get_media_properties_async()
    except Exception:
        return None
 
    timeline = target_session.get_timeline_properties()
    try:
        duration = (timeline.end_time - timeline.start_time).total_seconds()
        position = (timeline.position - timeline.start_time).total_seconds()
    except Exception:
        duration, position = 0.0, 0.0
 
    name = props.title or ""
    album = props.album_title or ""
    raw_artist = props.artist or ""
    artist = clean_artist(raw_artist, album)
    thumbnail_bytes = await read_thumbnail_bytes(props.thumbnail)
 
    if not name:
        return None
 
    return TrackInfo(name=name, artist=artist, album=album,
                      duration=max(duration, 0.0), position=max(position, 0.0),
                      thumbnail_bytes=thumbnail_bytes)
 
 
_artwork_cache: dict = {}
 
 
def _normalize_for_match(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[\(\[][^)\]]*[\)\]]", " ", text) 
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()
 
 
def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()
 
 
def _itunes_match_artwork_url(track: TrackInfo) -> Optional[str]:
    query = f"{track.artist} {track.name}".strip() or track.name
    params = urllib.parse.urlencode({"term": query, "entity": "song", "limit": 5})
    url = f"https://itunes.apple.com/search?{params}"
 
    wanted_name = _normalize_for_match(track.name)
    wanted_artist = _normalize_for_match(track.artist)
    wanted_album = _normalize_for_match(track.album)
 
    artwork_url = None
    best_score = 0.0
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results") or []
 
        best = None
        best_name_score = 0.0
        best_artist_score = 0.0
        best_album_score = 0.0
        for r in results:
            got_name = _normalize_for_match(r.get("trackName", ""))
            got_artist = _normalize_for_match(r.get("artistName", ""))
            got_album = _normalize_for_match(r.get("collectionName", ""))
            name_score = _similarity(wanted_name, got_name)
            artist_score = _similarity(wanted_artist, got_artist) if wanted_artist else 1.0
            album_score = _similarity(wanted_album, got_album) if wanted_album else 1.0
            score = (name_score * 0.5) + (artist_score * 0.3) + (album_score * 0.2)
            if score > best_score:
                best_score = score
                best = r
                best_name_score = name_score
                best_artist_score = artist_score
                best_album_score = album_score
 
        good_match = (
            best is not None
            and best_name_score >= 0.55
            and (best_artist_score >= 0.45 or not wanted_artist)
            and (best_album_score >= 0.45 or not wanted_album)
            and best_score >= 0.6
        )
        if good_match:
            raw = best.get("artworkUrl100")
            if raw:
                artwork_url = raw.replace("100x100bb", "600x600bb")
    except Exception:
        artwork_url = None
        best_score = 0.0
 
    return artwork_url
 
 
def _upload_exact_thumbnail(track: TrackInfo) -> Optional[str]:
    if not track.thumbnail_bytes:
        return None
    try:
        response = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": ("cover.jpg", track.thumbnail_bytes)},
            timeout=15,
        )
        response.raise_for_status()
        url = response.text.strip()
        if not url.startswith("http"):
            raise ValueError(f"unexpected response: {url!r}")
    except Exception:
        return None
 
    return url
 
 
def get_artwork_url(track: TrackInfo) -> Optional[str]:
    cache_key = (track.name, track.artist, track.album)
    if cache_key in _artwork_cache:
        return _artwork_cache[cache_key]
 
    artwork_url = _upload_exact_thumbnail(track)
    if not artwork_url:
        artwork_url = _itunes_match_artwork_url(track)
 
    _artwork_cache[cache_key] = artwork_url
    return artwork_url
 
 
def build_activity(track: TrackInfo, cfg: dict) -> dict:
    now = time.time()
    start_ts = int(now - track.position)
    end_ts = int(start_ts + track.duration) if track.duration > 0 else None
 
    activity = {
        "activity_type": ActivityType.LISTENING,
        "status_display_type": StatusDisplayType.STATE,
        "details": track.name,
        "state": track.artist if track.artist else "Apple Music",
        "start": start_ts,
    }
    if end_ts:
        activity["end"] = end_ts
 
    artwork_url = get_artwork_url(track)
    if artwork_url:
        activity["large_image"] = artwork_url
        if track.album:
            activity["large_text"] = track.album
 
    if cfg.get("show_profile_button") and cfg.get("profile_url"):
        activity["buttons"] = [{
            "label": cfg.get("profile_button_label", "Show Apple Music Profile"),
            "url": cfg["profile_url"],
        }]
 
    return activity
 
 
def main_loop():
    cfg = load_config()
    client_id = cfg["discord_client_id"]
    if not client_id or client_id == "YOUR_DISCORD_APPLICATION_ID":
        sys.exit(f"Set 'discord_client_id' in {CONFIG_PATH} first.")
 
    rpc = Presence(client_id)
    connected = False
    last_signature = None
 
    print("Watching Apple Music for playback... (Ctrl+C to stop)")
 
    while True:
        track = asyncio.run(get_now_playing(cfg["app_id_match"]))
 
        if track is None:
            if connected and last_signature is not None:
                try:
                    rpc.clear()
                except Exception:
                    pass
                last_signature = None
            time.sleep(cfg["poll_interval_seconds"])
            continue
 
        if not connected:
            try:
                rpc.connect()
                connected = True
            except Exception as e:
                print(f"Could not connect to Discord (is Discord running?): {e}")
                time.sleep(cfg["poll_interval_seconds"])
                continue
 
        has_end = track.duration > 0
        signature = (track.name, track.artist, has_end)
        if signature != last_signature:
            try:
                rpc.update(**build_activity(track, cfg))
                last_signature = signature
                print(f"Now showing: {track.name} - {track.artist}")
            except PyPresenceException as e:
                print(f"Discord update failed: {e}")
                connected = False
 
        time.sleep(cfg["poll_interval_seconds"])
 
 
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nStopped.")
# quickbars_bridge/hass_helpers.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from datetime import timedelta
import base64

from homeassistant.core import HomeAssistant
from homeassistant.helpers.network import get_url
from homeassistant.components import media_source
from homeassistant.components.media_player.browse_media import async_process_play_media_url
from homeassistant.components.http.auth import async_sign_path
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# ---------- Color ----------
def normalize_color_hex(color_in: Any) -> str | None:
    def _clamp8(x: int) -> int: return 0 if x < 0 else 255 if x > 255 else x
    if isinstance(color_in, (list, tuple)) and len(color_in) == 3:
        r,g,b = (_clamp8(int(color_in[0])), _clamp8(int(color_in[1])), _clamp8(int(color_in[2])))
        return f"#{r:02x}{g:02x}{b:02x}"
    if isinstance(color_in, dict) and all(k in color_in for k in ("r","g","b")):
        r,g,b = (_clamp8(int(color_in["r"])), _clamp8(int(color_in["g"])), _clamp8(int(color_in["b"])))
        return f"#{r:02x}{g:02x}{b:02x}"
    if isinstance(color_in, str) and color_in.strip():
        return color_in.strip()
    return None

# ---------- Iconify (mdi:*) ----------
async def mdi_svg_data_uri(hass: HomeAssistant, mdi_icon: str) -> tuple[str | None, str | None]:
    if not mdi_icon: return None, None
    icon_id = mdi_icon.strip().replace(":", "%3A")
    url = f"https://api.iconify.design/{icon_id}.svg"
    try:
        session = async_get_clientsession(hass)
        async with session.get(url, timeout=8) as resp:
            if resp.status != 200:
                return None, url
            svg_bytes = await resp.read()
        b64 = base64.b64encode(svg_bytes).decode()
        return f"data:image/svg+xml;base64,{b64}", url
    except Exception:
        return None, url

# ---------- Media helpers ----------
def ensure_still_image_url(u: str) -> str:
    if isinstance(u, str):
        u = u.replace("/api/camera_proxy_stream/", "/api/camera_proxy/")
        u = u.replace("/api/image_proxy_stream/", "/api/image_proxy/")
    return u

def media_id_from_selector(val: Any) -> str | None:
    if isinstance(val, dict):
        mid = val.get("media_content_id") or val.get("media_id")
        return str(mid) if mid else None
    if isinstance(val, str):
        return val
    return None

def selector_thumbnail(sel: Any) -> str | None:
    if isinstance(sel, dict):
        meta = sel.get("metadata")
        if isinstance(meta, dict):
            thumb = meta.get("thumbnail")
            if isinstance(thumb, str) and thumb:
                return thumb
    return None

async def abs_media_url(hass: HomeAssistant, spec: Any) -> str | None:
    if not spec: return None
    base = get_url(hass)

    def _abs_path(path: str) -> str:
        p = ensure_still_image_url(path)
        if p.startswith(("http://","https://")): return p
        if p.startswith("/api/"):
            signed = async_sign_path(hass, p, timedelta(seconds=60))
            return f"{base}{signed}"
        if p.startswith("/"): return f"{base}{p}"
        if p.startswith("local/"): return f"{base}/{p}"
        return p

    if isinstance(spec, str):
        return _abs_path(spec)

    if isinstance(spec, dict):
        if spec.get("url"):
            return spec["url"]
        if spec.get("path"):
            p = str(spec["path"]).lstrip("/")
            if not p.startswith("local/"):
                p = f"local/{p}"
            return _abs_path(p)
        mid = spec.get("media_id") or spec.get("media_content_id")
        if mid:
            play_item = await media_source.async_resolve_media(hass, str(mid), None)
            url = async_process_play_media_url(hass, play_item.url)
            return _abs_path(url)

    return None

# ---------- Notify payload ----------
async def build_notify_payload(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    # icon
    icon_svg, icon_url = await mdi_svg_data_uri(hass, data.get("mdi_icon"))

    # image
    img_url = None
    img_sel = data.get("image_media")
    if img_sel and not data.get("image"):
        thumb = selector_thumbnail(img_sel)
        if thumb:
            img_url = await abs_media_url(hass, thumb)
        else:
            mid = media_id_from_selector(img_sel)
            if mid:
                tmp = await abs_media_url(hass, {"media_id": mid})
                img_url = ensure_still_image_url(tmp or "")
    if img_url is None:
        img_spec = data.get("image")
        if isinstance(img_spec, dict) and ("media_id" in img_spec or "media_content_id" in img_spec):
            mid = img_spec.get("media_id") or img_spec.get("media_content_id")
            if mid:
                tmp = await abs_media_url(hass, {"media_id": mid})
                img_url = ensure_still_image_url(tmp or "")
            else:
                img_url = await abs_media_url(hass, img_spec)
        else:
            img_url = await abs_media_url(hass, img_spec)

    # sound
    snd_url = None
    snd_sel = data.get("sound_media")
    if snd_sel and not data.get("sound"):
        mid = media_id_from_selector(snd_sel)
        if mid:
            snd_url = await abs_media_url(hass, {"media_id": mid})
    if snd_url is None:
        snd_spec = data.get("sound")
        if isinstance(snd_spec, dict) and ("media_id" in snd_spec or "media_content_id" in snd_spec):
            mid = snd_spec.get("media_id") or snd_spec.get("media_content_id")
            if mid:
                snd_url = await abs_media_url(hass, {"media_id": mid})
            else:
                snd_url = await abs_media_url(hass, snd_spec)
        else:
            snd_url = await abs_media_url(hass, snd_spec)

    # sound volume
    sound_pct = None
    if isinstance(data.get("sound"), dict) and "volume_percent" in data["sound"]:
        try: sound_pct = int(data["sound"]["volume_percent"])
        except Exception: sound_pct = None
    elif "sound_volume_percent" in data:
        try: sound_pct = int(data["sound_volume_percent"])
        except Exception: sound_pct = None
    if sound_pct is not None:
        sound_pct = max(0, min(200, sound_pct))

    # duration
    try:
        chosen_duration = int(data.get("length")) if str(data.get("length","")).strip() != "" else 6
    except Exception:
        chosen_duration = 6
    chosen_duration = max(3, min(120, chosen_duration))

    payload: Dict[str, Any] = {
        "title":        data.get("title"),
        "message":      data.get("message"),
        "actions":      data.get("actions") or [],
        "duration":     chosen_duration,
        "position":     data.get("position"),
        "color":        normalize_color_hex(data.get("color")),
        "transparency": data.get("transparency"),
        "interrupt":    bool(data.get("interrupt", False)),
        "image_url":    img_url,
        "sound_url":    snd_url,
        "sound_volume_percent": sound_pct,
        "icon_svg_data_uri": icon_svg,
        "icon_url":     icon_url,
    }
    # strip nulls/empties
    return {k: v for k, v in payload.items() if v not in (None, "", [])}

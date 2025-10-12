# src/quickbars_bridge/qb.py

from __future__ import annotations
from typing import Iterable, Dict, Any, Set, List, Tuple

def unique_qb_name(base: str, existing_names: Iterable[str]) -> str:
    """Return 'Base N' not present (case-insensitive) in existing_names."""
    ci: Set[str] = { (n or "").strip().casefold() for n in existing_names }
    i = 1
    while True:
        candidate = f"{base} {i}"
        if candidate.casefold() not in ci:
            return candidate
        i += 1

def default_quickbar(name: str) -> Dict[str, Any]:
    """Default QuickBar shape used by the app (keep this single source of truth)."""
    return {
        "name": name,
        "savedEntityIds": [],
        "showNameInOverlay": True,
        "showTimeOnQuickBar": True,
        "backgroundColor": "colorSurface",
        "backgroundOpacity": 90,
        "onStateColor": "colorPrimary",
        "position": "RIGHT",
        "useGridLayout": False,
        "autoCloseQuickBarDomains": [],
        "customBackgroundColor": [24,24,24],
        "customOnStateColor": [255,204,0],
        "haTriggerAlias": "",
    }


def saved_options_from_snapshot(snapshot: Dict[str, Any] | None) -> Tuple[List[Dict[str,str]], List[str]]:
    """Build (options, saved_ids) used by the selector from the snapshot dict."""
    entities = list((snapshot or {}).get("entities", []) or [])
    saved = [e for e in entities if e.get("isSaved") and e.get("id")]
    def _label(e: Dict[str, Any]) -> str:
        n = e.get("customName") or e.get("friendlyName") or e["id"]
        return f"{n} ({e['id']})"
    options = [{"label": _label(e), "value": e["id"]} for e in saved]
    return options, [e["id"] for e in saved]

def defaults_from_qb(qb: Dict[str, Any]) -> Dict[str, Any]:
    """Map a QuickBar dict into a single defaults dict used to render the form."""
    return {
        "name": qb.get("name") or "",
        "savedEntityIds": list(qb.get("savedEntityIds") or []),
        "showNameInOverlay": bool(qb.get("showNameInOverlay", True)),
        "showTimeOnQuickBar": bool(qb.get("showTimeOnQuickBar", True)),
        "autoCloseQuickBarDomains": list(qb.get("autoCloseQuickBarDomains") or []),
        "position": (qb.get("position") or "RIGHT").upper(),
        "useGridLayout": bool(qb.get("useGridLayout", False)),
        "backgroundOpacity": int(qb.get("backgroundOpacity", 90)),
        "backgroundColor": qb.get("backgroundColor") or "colorSurface",
        "customBackgroundColor": list(qb.get("customBackgroundColor") or [24, 24, 24]),
        "onStateColor": qb.get("onStateColor") or "colorPrimary",
        "customOnStateColor": list(qb.get("customOnStateColor") or [255, 204, 0]),
        "haTriggerAlias": qb.get("haTriggerAlias") or "",
    }

def normalize_saved_entities(requested: List[str] | None, saved_ids: List[str], current: List[str]) -> List[str]:
    """Preserve order, restrict to saved_ids, and dedupe."""
    req = list(requested or current)
    seen, norm = set(), []
    for eid in req:
        if eid in saved_ids and eid not in seen:
            norm.append(eid); seen.add(eid)
    return norm

def name_taken(new_name: str, qb_list: List[Dict[str, Any]], exclude_index: int) -> bool:
    """Case-insensitive check that excludes the current QB index."""
    if not new_name:
        return False
    ci = {
        (x.get("name") or "").strip().casefold()
        for i, x in enumerate(qb_list) if i != exclude_index
    }
    return new_name.strip().casefold() in ci

def attempted_from_user(cur: Dict[str, Any], user_input: Dict[str, Any], saved_ids: List[str]) -> Dict[str, Any]:
    """Produce the attempted 'defaults' to re-render the form after validation fails."""
    attempted = dict(cur)
    attempted["name"] = (user_input.get("quickbar_name", cur["name"]) or "").strip() or cur["name"]
    attempted["savedEntityIds"] = normalize_saved_entities(user_input.get("saved_entities"), saved_ids, cur["savedEntityIds"])
    attempted["showNameInOverlay"] = bool(user_input.get("show_name_on_overlay", cur["showNameInOverlay"]))
    attempted["showTimeOnQuickBar"] = bool(user_input.get("show_time_on_quickbar", cur["showTimeOnQuickBar"]))
    attempted["haTriggerAlias"] = user_input.get("ha_trigger_alias", cur["haTriggerAlias"])
    attempted["autoCloseQuickBarDomains"] = list(user_input.get("auto_close_domains") or cur["autoCloseQuickBarDomains"])

    pos = (user_input.get("position", cur["position"]) or "RIGHT").upper()
    req_grid = bool(user_input.get("use_grid_layout", cur["useGridLayout"]))
    attempted["position"] = pos
    attempted["useGridLayout"] = (req_grid and pos in ("LEFT", "RIGHT"))

    attempted["backgroundOpacity"] = int(user_input.get("background_opacity", cur["backgroundOpacity"]))

    use_bg = bool(user_input.get("use_custom_bg", (cur["backgroundColor"] == "custom")))
    if use_bg:
        attempted["backgroundColor"] = "custom"
        attempted["customBackgroundColor"] = list(user_input.get("bg_rgb") or cur["customBackgroundColor"])
    else:
        attempted["backgroundColor"] = cur["backgroundColor"] if cur["backgroundColor"] != "custom" else "colorSurface"

    use_on = bool(user_input.get("use_custom_on_state", (cur["onStateColor"] == "custom")))
    if use_on:
        attempted["onStateColor"] = "custom"
        attempted["customOnStateColor"] = list(user_input.get("on_rgb") or cur["customOnStateColor"])
    else:
        attempted["onStateColor"] = cur["onStateColor"] if cur["onStateColor"] != "custom" else "colorPrimary"

    return attempted

def apply_edits(qb: Dict[str, Any], cur: Dict[str, Any], user_input: Dict[str, Any], saved_ids: List[str]) -> None:
    """Mutate `qb` in-place based on `user_input` following the same rules used for attempted."""
    qb["name"] = (user_input.get("quickbar_name", cur["name"]) or "").strip() or cur["name"]
    qb["savedEntityIds"] = normalize_saved_entities(user_input.get("saved_entities"), saved_ids, cur["savedEntityIds"])
    qb["showNameInOverlay"] = bool(user_input.get("show_name_on_overlay", cur["showNameInOverlay"]))
    qb["showTimeOnQuickBar"] = bool(user_input.get("show_time_on_quickbar", cur["showTimeOnQuickBar"]))
    qb["haTriggerAlias"] = user_input.get("ha_trigger_alias", cur["haTriggerAlias"])
    qb["autoCloseQuickBarDomains"] = list(user_input.get("auto_close_domains") or cur["autoCloseQuickBarDomains"])

    pos = (user_input.get("position", cur["position"]) or "RIGHT").upper()
    req_grid = bool(user_input.get("use_grid_layout", cur["useGridLayout"]))
    qb["position"] = pos
    qb["useGridLayout"] = (req_grid and pos in ("LEFT", "RIGHT"))

    qb["backgroundOpacity"] = int(user_input.get("background_opacity", cur["backgroundOpacity"]))

    use_bg = bool(user_input.get("use_custom_bg", (cur["backgroundColor"] == "custom")))
    if use_bg:
        qb["backgroundColor"] = "custom"
        qb["customBackgroundColor"] = list(user_input.get("bg_rgb") or cur["customBackgroundColor"])
    else:
        qb["backgroundColor"] = cur["backgroundColor"] if cur["backgroundColor"] != "custom" else "colorSurface"
        qb.pop("customBackgroundColor", None)

    use_on = bool(user_input.get("use_custom_on_state", (cur["onStateColor"] == "custom")))
    if use_on:
        qb["onStateColor"] = "custom"
        qb["customOnStateColor"] = list(user_input.get("on_rgb") or cur["customOnStateColor"])
    else:
        qb["onStateColor"] = cur["onStateColor"] if cur["onStateColor"] != "custom" else "colorPrimary"
        qb.pop("customOnStateColor", None)
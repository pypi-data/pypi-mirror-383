# src/quickbars_bridge/hass_flow.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import voluptuous as vol
from homeassistant.helpers.selector import selector
from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant, State

# Exported so the integration doesn't carry this list
ALLOWED_ENTITY_DOMAINS: List[str] = [
    "light", "switch", "button", "fan", "input_boolean", "input_button",
    "script", "scene", "automation", "camera",
    "climate", "cover", "lock", "media_player",
    "sensor", "binary_sensor", "alarm_control_panel",
]

# ---------- Generic small helpers ----------

def mask_token(s: str | None, keep_prefix: int = 3, keep_suffix: int = 2) -> str:
    if not s:
        return "<none>"
    if len(s) <= keep_prefix + keep_suffix:
        return s[0] + "***" + s[-1]
    return f"{s[:keep_prefix]}***{s[-keep_suffix:]}"

def default_ha_url(hass: HomeAssistant) -> str:
    try:
        return get_url(hass) or ""
    except Exception:
        return ""

def decode_zeroconf(discovery_info: Any) -> Tuple[str | None, int | None, Dict[str, str], str | None, str | None]:
    """Return (host, port, props:str->str, hostname, name) from either object or dict shapes."""
    if hasattr(discovery_info, "host"):
        host = getattr(discovery_info, "host", None)
        port = getattr(discovery_info, "port", None)
        props_raw = dict(getattr(discovery_info, "properties", {}) or {})
        hostname = getattr(discovery_info, "hostname", None)
        name = getattr(discovery_info, "name", None)
    else:
        host = (discovery_info or {}).get("host")
        port = (discovery_info or {}).get("port")
        props_raw = dict((discovery_info or {}).get("properties") or {})
        hostname = (discovery_info or {}).get("hostname")
        name = (discovery_info or {}).get("name")

    props: dict[str, str] = {}
    for k, v in props_raw.items():
        key = k.decode() if isinstance(k, (bytes, bytearray)) else str(k)
        val = v.decode() if isinstance(v, (bytes, bytearray)) else str(v)
        props[key] = val
    return host, port, props, hostname, name

def map_entity_display_names(hass: HomeAssistant, entity_ids: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for eid in entity_ids:
        st: State | None = hass.states.get(eid)
        out[eid] = (st.name if (st and st.name) else eid.split(".", 1)[-1])
    return out

# ---------- Menu / simple step schemas ----------

def schema_menu() -> vol.Schema:
    return vol.Schema({
        vol.Required("action"): vol.In({
            "export": "Add / Remove Saved Entities",
            "manage_saved": "Manage Saved Entities",
            "manage_qb": "Manage QuickBars",
        })
    })

def schema_pair() -> vol.Schema:
    return vol.Schema({vol.Required("code"): str})

def schema_token(default_url: str, default_token: str | None = None) -> vol.Schema:
    return vol.Schema({
        vol.Required("url", default=default_url or ""): str,
        vol.Required("token", default=default_token or ""): str,
    })

def schema_expose(saved_ids: List[str]) -> vol.Schema:
    return vol.Schema({
        vol.Required("saved", default=list(saved_ids)): selector({
            "entity": {"multiple": True, "domain": ALLOWED_ENTITY_DOMAINS}
        })
    })

# ---------- Pick lists for 'manage saved' and 'manage quickbars' ----------

def saved_pick_options(snapshot: Dict[str, Any] | None) -> List[Dict[str, str]]:
    ents = [
        e for e in ((snapshot or {}).get("entities") or [])
        if e.get("isSaved") and e.get("id")
    ]
    def _label(e: Dict[str, Any]) -> str:
        return f"{e.get('customName') or e.get('friendlyName') or e['id']} ({e['id']})"
    return [{"label": _label(e), "value": e["id"]} for e in ents]

def schema_manage_saved_pick(options: List[Dict[str, str]], default_id: str) -> vol.Schema:
    return vol.Schema({
        vol.Required("entity", default=default_id): selector({
            "select": {"options": options, "mode": "dropdown"}
        })
    })

def qb_pick_options(qb_list: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for idx, qb in enumerate(qb_list):
        name = qb.get("name") or f"QuickBar {idx+1}"
        out.append({"label": name, "value": str(idx)})
    out.append({"label": "➕ New QuickBar", "value": "new"})
    return out

def schema_qb_pick(options: List[Dict[str, str]], default_idx: int) -> vol.Schema:
    return vol.Schema({
        vol.Required("quickbar", default=str(default_idx)): selector({
            "select": {"options": options, "mode": "dropdown"}
        })
    })

# ---------- Manage QuickBar (same schema you had, factored) ----------

def schema_qb_manage(qb: Dict[str, Any], saved_opts: List[Dict[str, str]], defaults: Dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required("quickbar_name", default=defaults["name"]): str,

        vol.Optional("saved_entities", default=defaults["savedEntityIds"]): selector({
            "select": {"options": saved_opts, "multiple": True}
        }),

        vol.Required("show_name_on_overlay", default=defaults["showNameInOverlay"]): selector({"boolean": {}}),
        vol.Required("show_time_on_quickbar", default=defaults["showTimeOnQuickBar"]): selector({"boolean": {}}),

        vol.Optional("ha_trigger_alias", default=qb.get("haTriggerAlias", "")): str,

        vol.Optional("auto_close_domains", default=defaults["autoCloseQuickBarDomains"]): selector({
            "select": {
                "options": [
                    "light","switch","button","input_boolean","input_button",
                    "script","scene","automation","camera"
                ],
                "multiple": True
            }
        }),

        vol.Required("position", default=defaults["position"]): selector({
            "select": {
                "options": [
                    {"label": "Right",  "value": "RIGHT"},
                    {"label": "Left",   "value": "LEFT"},
                    {"label": "Top",    "value": "TOP"},
                    {"label": "Bottom", "value": "BOTTOM"},
                ],
                "mode": "dropdown"
            }
        }),

        vol.Required("use_grid_layout", default=defaults["useGridLayout"]): selector({"boolean": {}}),

        vol.Required("background_opacity", default=defaults["backgroundOpacity"]): selector({
            "number": {"min": 0, "max": 100, "step": 1, "mode": "slider"}
        }),

        vol.Required("use_custom_bg", default=(qb.get("backgroundColor") == "custom")): selector({"boolean": {}}),
        vol.Optional("bg_rgb", default=list(qb.get("customBackgroundColor") or [24, 24, 24])): selector({"color_rgb": {}}),

        vol.Required("use_custom_on_state", default=(qb.get("onStateColor") == "custom")): selector({"boolean": {}}),
        vol.Optional("on_rgb", default=list(qb.get("customOnStateColor") or [255, 204, 0])): selector({"color_rgb": {}}),
    })

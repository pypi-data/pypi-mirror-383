from __future__ import annotations
from typing import Any, Mapping, Optional
import aiohttp

class QuickBarsClient:
    def __init__(self, host: str, port: int, *, timeout: float = 15.0) -> None:
        self._base = f"http://{host}:{port}"
        self._timeout = timeout

    async def _request_json(self, method: str, path: str, *, json: Any | None = None) -> Any:
        url = f"{self._base}{path}"
        async with aiohttp.ClientSession() as s:
            async with s.request(method, url, json=json, timeout=self._timeout) as r:
                r.raise_for_status()
                return await r.json()

    # ---- pairing / credentials ----
    async def get_pair_code(self) -> dict[str, Any]:
        return await self._request_json("GET", "/api/pair/code")

    async def confirm_pair(self, code: str, sid: str, *, ha_instance: str | None = None,
                           ha_name: str | None = None, ha_url: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": code, "sid": sid}
        if ha_instance: payload["ha_instance"] = ha_instance
        if ha_name:     payload["ha_name"] = ha_name
        if ha_url:      payload["ha_url"] = ha_url
        return await self._request_json("POST", "/api/pair/confirm", json=payload)

    async def set_credentials(self, url: str, token: str) -> dict[str, Any]:
        return await self._request_json("POST", "/api/ha/credentials", json={"url": url, "token": token})

    # ---- snapshot (authorized) ----
    async def get_snapshot(self) -> dict[str, Any]:
        return await self._request_json("GET", "/api/snapshot")

    async def post_snapshot(self, snapshot: dict[str, Any]) -> None:
        await self._request_json("POST", "/api/snapshot", json=snapshot)

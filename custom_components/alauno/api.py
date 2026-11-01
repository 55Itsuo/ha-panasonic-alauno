"""Minimal async client for the Alauno cloud (reverse engineered)."""
from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp

from .const import (
    API_BASE,
    AUDIENCE,
    AUTH_HOST,
    CLIENT_ID,
    REDIRECT_URI,
    SCOPE,
    USER_AGENT,
)

JST = timezone(timedelta(hours=9))


class AlaunoAuthError(Exception):
    """Authentication failed (token invalid / revoked)."""


class AlaunoApiError(Exception):
    """Any other API failure."""


def new_pkce() -> tuple[str, str]:
    """Return (verifier, challenge)."""
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def build_authorize_url(challenge: str, state: str) -> str:
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPE,
        "audience": AUDIENCE,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    return f"{AUTH_HOST}/authorize?{urlencode(params)}"


def extract_code(text: str) -> str:
    """Accept a full callback URL or a bare code."""
    text = text.strip()
    if "code=" in text:
        q = parse_qs(urlparse(text).query)
        if "code" in q:
            return q["code"][0]
        # fallback: fragment/odd formats
        return parse_qs(text.split("?", 1)[-1])["code"][0]
    return text


def parse_time(value: str) -> datetime:
    """'20261030192348+0900' -> aware datetime."""
    return datetime.strptime(value, "%Y%m%d%H%M%S%z")


async def exchange_code(
    session: aiohttp.ClientSession, code: str, verifier: str
) -> dict:
    return await _token(
        session,
        {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": REDIRECT_URI,
        },
    )


async def refresh(session: aiohttp.ClientSession, refresh_token: str) -> dict:
    return await _token(
        session,
        {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token,
        },
    )


async def _token(session: aiohttp.ClientSession, body: dict) -> dict:
    async with session.post(
        f"{AUTH_HOST}/oauth/token",
        json=body,
        headers={"User-Agent": USER_AGENT},
    ) as resp:
        data = await resp.json(content_type=None)
        if resp.status in (400, 401, 403):
            raise AlaunoAuthError(str(data.get("error_description") or data))
        if resp.status != 200:
            raise AlaunoApiError(f"token endpoint {resp.status}")
        return data


class AlaunoClient:
    """Holds tokens and calls the REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        refresh_token: str,
        on_new_refresh_token=None,
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._refresh_token = refresh_token
        self._on_new_refresh_token = on_new_refresh_token
        self._access_token: str | None = None
        self._expires: datetime = datetime.min.replace(tzinfo=timezone.utc)

    async def _ensure_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._access_token and now < self._expires - timedelta(minutes=5):
            return self._access_token
        data = await refresh(self._session, self._refresh_token)
        self._access_token = data["access_token"]
        self._expires = now + timedelta(seconds=int(data.get("expires_in", 3600)))
        new_rt = data.get("refresh_token")
        if new_rt and new_rt != self._refresh_token:
            self._refresh_token = new_rt
            if self._on_new_refresh_token:
                self._on_new_refresh_token(new_rt)
        return self._access_token

    async def _get(self, path: str, params: dict | None = None) -> dict:
        for attempt in (1, 2):
            token = await self._ensure_token()
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {token}",
                "x-api-key": self._api_key,
                "x-timestamp": datetime.now(JST).strftime("%Y%m%d%H%M%S+0900"),
                "User-Agent": USER_AGENT,
            }
            async with self._session.get(
                f"{API_BASE}{path}", params=params, headers=headers
            ) as resp:
                if resp.status == 401 and attempt == 1:
                    self._access_token = None
                    continue
                if resp.status in (401, 403):
                    raise AlaunoAuthError(f"{path}: {resp.status}")
                if resp.status != 200:
                    raise AlaunoApiError(f"{path}: {resp.status}")
                return await resp.json(content_type=None)
        raise AlaunoApiError("unreachable")

    async def devices(self) -> list[dict]:
        data = await self._get("/devices/info")
        return data.get("devices", [])

    async def care(self, appliance_id: str) -> list[dict]:
        data = await self._get("/care/info", {"appliance_id": appliance_id})
        devs = data.get("devices", [])
        return devs[0].get("cares", []) if devs else []

    async def usages(self, day: datetime) -> dict[str, list[datetime]]:
        """appliance_id -> usage datetimes for the given JST day."""
        date = day.astimezone(JST).strftime("%Y%m%d000000+0900")
        data = await self._get("/mimamori/records", {"date": date})
        out: dict[str, list[datetime]] = {}
        for rec in data.get("records", []):
            times = [
                parse_time(u["times"])
                for u in (rec.get("usages") or [])
                if u.get("times")
            ]
            out[rec["mimamori_id"]] = times
        return out

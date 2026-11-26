# language: Python 3.11 — core/session.py
import os

import aiohttp

from config import PROXY_FILE, USER_AGENT

_session: aiohttp.ClientSession | None = None


def _load_proxies() -> list[str]:
    if not os.path.exists(PROXY_FILE):
        return []
    with open(PROXY_FILE) as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


async def init_session():
    global _session
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }
    _session = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False, limit=0),
        headers=headers,
        cookie_jar=aiohttp.CookieJar(unsafe=True),
    )
    return _session


def get_session() -> aiohttp.ClientSession:
    if _session is None:
        raise RuntimeError("session not initialized — call init_session() first")
    return _session


async def close_session():
    global _session
    if _session is not None:
        await _session.close()
        _session = None


def proxies_available() -> list[str]:
    return _load_proxies()

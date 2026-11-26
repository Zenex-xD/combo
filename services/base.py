# language: Python 3.11 — services/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import aiohttp


class Status(str, Enum):
    HIT = "HIT"
    INVALID = "INVALID"
    TWOFA = "2FA"
    LOCKED = "LOCKED"
    ERROR = "ERROR"


@dataclass
class CheckResult:
    service: str
    email: str
    status: Status
    detail: str = ""


class BaseService(ABC):
    name: str = ""

    @abstractmethod
    async def check(self, session: aiohttp.ClientSession, email: str, pw: str) -> CheckResult:
        ...

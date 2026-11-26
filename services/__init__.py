# language: Python 3.11 — services/__init__.py (updated)
from .amazon import AmazonService
from .prime import PrimeService
from .steam import SteamService
from .epic import EpicService
from .netflix import NetflixService

SERVICES = {
    "amazon": AmazonService(),
    "prime": PrimeService(),
    "steam": SteamService(),
    "epic": EpicService(),
    "netflix": NetflixService(),
}

__all__ = ["SERVICES", "BaseService", "CheckResult", "Status"]

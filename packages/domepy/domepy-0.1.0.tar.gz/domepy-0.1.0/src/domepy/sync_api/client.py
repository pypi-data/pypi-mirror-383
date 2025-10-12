from httpx import Client
from .polymarket import Polymarket
from contextlib import contextmanager

__all__ = ["syncdome"]


class Dome:
    def __init__(self, client: Client):
        self.polymarket = Polymarket(client)


@contextmanager
def syncdome():
    with Client() as client:
        yield Dome(client)

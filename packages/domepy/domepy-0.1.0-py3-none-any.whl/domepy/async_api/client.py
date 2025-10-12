from httpx import AsyncClient
from .polymarket import Polymarket
from contextlib import asynccontextmanager

__all__ = ["asyncdome"]


class AsyncDome:
    def __init__(self, client: AsyncClient):
        self.polymarket = Polymarket(client)


@asynccontextmanager
async def asyncdome():
    async with AsyncClient() as client:
        yield AsyncDome(client)

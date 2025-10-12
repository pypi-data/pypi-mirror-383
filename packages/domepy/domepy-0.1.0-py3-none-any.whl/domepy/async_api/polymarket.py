from typing import Literal, Unpack
from domepy.core.schema import (
    CandlesticksResponse,
    OrdersParams,
    OrdersResponse,
    MarketPriceParams,
    MarketPriceResponse,
    CandlesticksParams,
)
from httpx import AsyncClient, QueryParams


class Polymarket:
    BASE_URL: Literal["https://api.domeapi.io/v1/polymarket"] = (
        "https://api.domeapi.io/v1/polymarket"
    )

    def __init__(self, client: AsyncClient):
        self._client = client

    async def orders(self, **params: Unpack[OrdersParams]) -> OrdersResponse:
        response = await self._client.get(
            self.BASE_URL + "/orders", params=QueryParams(**params)
        )

        return OrdersResponse(**response.json())

    async def market_price(
        self, token_id: str, **params: Unpack[MarketPriceParams]
    ) -> MarketPriceResponse:
        response = await self._client.get(
            self.BASE_URL + "/market-price/" + token_id, params=QueryParams(**params)
        )

        return MarketPriceResponse(**response.json())

    async def candlesticks(
        self, condition_id: str, **params: Unpack[CandlesticksParams]
    ) -> CandlesticksResponse:
        response = await self._client.get(
            self.BASE_URL + "/market-price/" + condition_id,
            params=QueryParams(**params),
        )

        return CandlesticksResponse(**response.json())

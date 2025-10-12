from typing import Literal, Unpack
from domepy.core.schema import (
    CandlesticksResponse,
    OrdersParams,
    OrdersResponse,
    MarketPriceParams,
    MarketPriceResponse,
    CandlesticksParams,
)
from httpx import Client, QueryParams


class Polymarket:
    BASE_URL: Literal["https://api.domeapi.io/v1/polymarket"] = (
        "https://api.domeapi.io/v1/polymarket"
    )

    def __init__(self, client: Client):
        self._client = client

    def orders(self, **params: Unpack[OrdersParams]) -> OrdersResponse:
        response = self._client.get(
            self.BASE_URL + "/orders", params=QueryParams(**params)
        )

        return OrdersResponse(**response.json())

    def market_price(
        self, token_id: str, **params: Unpack[MarketPriceParams]
    ) -> MarketPriceResponse:
        response = self._client.get(
            self.BASE_URL + "/market-price/" + token_id, params=QueryParams(**params)
        )

        return MarketPriceResponse(**response.json())

    def candlesticks(
        self, condition_id: str, **params: Unpack[CandlesticksParams]
    ) -> CandlesticksResponse:
        response = self._client.get(
            self.BASE_URL + "/market-price/" + condition_id,
            params=QueryParams(**params),
        )

        return CandlesticksResponse(**response.json())

from typing import Literal
from pydantic import BaseModel, Field
from typing import TypedDict
import datetime

__all__ = [
    "DomeSDKConfig",
    "RequestConfig",
    "MarketPriceResponse",
    "MarketPriceParams",
    "CandlestickPrice",
    "CandlestickAskBid",
    "CandlestickData",
    "TokenMetadata",
    "CandlesticksResponse",
    "CandlesticksParams",
    "PnLDataPoint",
    "WalletPnLResponse",
    "GetWalletPnLParams",
    "Order",
    "Pagination",
    "OrdersResponse",
    "OrdersParams",
    "KalshiMarket",
    "PolymarketMarket",
    "MarketData",
    "MatchingMarketsResponse",
    "GetMatchingMarketsParams",
    "GetMatchingMarketsBySportParams",
    "MatchingMarketsBySportResponse",
    "ApiError",
    "ValidationError",
    "HTTPMethod",
]

HTTPMethod = Literal["GET", "POST", "PUT", "DELETE"]


class DomeSDKConfig(TypedDict, total=False):
    api_key: str | None
    base_url: str | None
    timeout: float | None


class RequestConfig(TypedDict, total=False):
    timeout: float | None
    headers: dict[str, str] | None


class MarketPriceResponse(BaseModel):
    price: float = Field(..., description="Current market price")
    at_time: datetime.datetime = Field(..., description="Timestamp of the price data")


class MarketPriceParams(TypedDict, total=False):
    at_time: int | None


class CandlestickPrice(BaseModel):
    open: float
    high: float
    low: float
    close: float
    open_dollars: str
    high_dollars: str
    low_dollars: str
    close_dollars: str
    mean: float
    mean_dollars: str
    previous: float
    previous_dollars: str


class CandlestickAskBid(BaseModel):
    open: float
    close: float
    high: float
    low: float
    open_dollars: str
    close_dollars: str
    high_dollars: str
    low_dollars: str


class CandlestickData(BaseModel):
    end_period_ts: int
    open_interest: int
    price: CandlestickPrice
    volume: int
    yes_ask: CandlestickAskBid
    yes_bid: CandlestickAskBid


class TokenMetadata(BaseModel):
    token_id: str


class CandlesticksResponse(BaseModel):
    candlesticks: list[list[CandlestickData | TokenMetadata]]


class CandlesticksParams(TypedDict, total=False):
    start_time: int
    end_time: int
    interval: Literal[1, 60, 1440] | None


class PnLDataPoint(BaseModel):
    timestamp: datetime.datetime
    pnl_to_date: float


class WalletPnLResponse(BaseModel):
    granularity: str
    start_time: int
    end_time: int
    wallet_address: str
    pnl_over_time: list[PnLDataPoint]


class GetWalletPnLParams(TypedDict, total=False):
    wallet_address: str
    granularity: Literal["day", "week", "month", "year", "all"]
    start_time: int | None
    end_time: int | None


class Order(BaseModel):
    token_id: str
    side: Literal["BUY", "SELL"]
    market_slug: str
    condition_id: str
    shares: int
    shares_normalized: float
    price: float
    tx_hash: str
    title: str
    timestamp: datetime.datetime
    order_hash: str
    user: str


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


class OrdersResponse(BaseModel):
    orders: list[Order]
    pagination: Pagination


class OrdersParams(TypedDict, total=False):
    market_slug: str | None
    condition_id: str | None
    token_id: str | None
    start_time: int | None
    end_time: int | None
    limit: int | None
    offset: int | None
    user: str | None


class KalshiMarket(BaseModel):
    platform: Literal["KALSHI"]
    event_ticker: str
    market_tickers: list[str]


class PolymarketMarket(BaseModel):
    platform: Literal["POLYMARKET"]
    market_slug: str
    token_ids: list[str]


MarketData = KalshiMarket | PolymarketMarket


class MatchingMarketsResponse(BaseModel):
    markets: dict[str, list[MarketData]]


class GetMatchingMarketsParams(TypedDict, total=False):
    polymarket_market_slug: list[str] | None
    kalshi_event_ticker: list[str] | None


class GetMatchingMarketsBySportParams(TypedDict, total=False):
    sport: Literal["nfl", "mlb"]
    date: str


class MatchingMarketsBySportResponse(BaseModel):
    markets: dict[str, list[MarketData]]
    sport: str
    date: str


class ApiError(BaseModel):
    error: str
    message: str


class ValidationError(ApiError):
    required: str | None = None

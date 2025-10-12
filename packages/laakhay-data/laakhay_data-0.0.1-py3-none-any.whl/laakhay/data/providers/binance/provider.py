"""Binance exchange data provider."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time

from ...core import BaseProvider, InvalidIntervalError, InvalidSymbolError, TimeInterval, MarketType
from ...models import Candle, FundingRate, OpenInterest, OrderBook, Symbol, Trade
from ...utils import HTTPClient, retry_async
from .constants import BASE_URLS, INTERVAL_MAP as BINANCE_INTERVAL_MAP, OI_PERIOD_MAP
from .websocket_mixin import BinanceWebSocketMixin

logger = logging.getLogger(__name__)


class BinanceProvider(BinanceWebSocketMixin, BaseProvider):
    """Binance exchange data provider.
    
    Supports both Spot and Futures markets via market_type parameter.
    Default is SPOT for backward compatibility.
    
    Args:
        market_type: Market type (SPOT or FUTURES)
        api_key: Optional API key for authenticated endpoints
        api_secret: Optional API secret for authenticated endpoints

    """

    # REST and interval configuration (WebSocket config lives in constants + mixin)
    # Back-compat: expose INTERVAL_MAP at class level for tests/consumers
    INTERVAL_MAP = BINANCE_INTERVAL_MAP

    def __init__(
        self,
        market_type: MarketType = MarketType.SPOT,
        api_key: Optional[str] = None, 
        api_secret: Optional[str] = None,
        symbols_cache_ttl: float = 300.0,
        products_cache_ttl: float = 600.0,
    ) -> None:
        super().__init__(name=f"binance-{market_type.value}")
        self.market_type = market_type
        self._base_url = BASE_URLS[market_type]
        self._http = HTTPClient(base_url=self._base_url)
        self._api_key = api_key
        self._api_secret = api_secret
        # Install Binance rate-limit aware response hook
        self._http.add_response_hook(self._binance_rate_limit_hook)
        # Symbols cache (full list); filter by quote_asset on read
        self._symbols_cache: Optional[List[Symbol]] = None
        self._symbols_cache_ts: Optional[float] = None
        self._symbols_cache_ttl = symbols_cache_ttl
        # Products cache (Binance bapi)
        self._products_cache: Optional[List[Dict[str, Any]]] = None
        self._products_cache_ts: Optional[float] = None
        self._products_cache_ttl = products_cache_ttl

    def set_credentials(self, api_key: str, api_secret: str) -> None:
        """Set API credentials for authenticated endpoints."""
        self._api_key = api_key
        self._api_secret = api_secret

    @property
    def has_credentials(self) -> bool:
        """Check if API credentials are set."""
        return bool(self._api_key and self._api_secret)

    def _get_klines_endpoint(self) -> str:
        """Get the klines endpoint for the market type."""
        if self.market_type == MarketType.FUTURES:
            return "/fapi/v1/klines"
        return "/api/v3/klines"
    
    def _get_exchange_info_endpoint(self) -> str:
        """Get the exchange info endpoint for the market type."""
        if self.market_type == MarketType.FUTURES:
            return "/fapi/v1/exchangeInfo"
        return "/api/v3/exchangeInfo"

    def validate_interval(self, interval: TimeInterval) -> None:
        """Validate interval is supported by Binance."""
        if interval not in self.INTERVAL_MAP:
            raise InvalidIntervalError(f"Interval {interval} not supported by Binance")

    # ----------------------
    # Rate limit handling
    # ----------------------
    _WEIGHT_LIMITS = {
        # Conservative defaults; actual limits come from exchangeInfo rateLimits
        # REQUEST_WEIGHT per minute commonly 1200 on Spot, and higher on futures
        "1m": 1200,
        "10s": 300,  # Futures commonly 300 per 10s window; used heuristically
    }

    def _estimate_weight_budget(self, headers: Dict[str, str]) -> Optional[float]:
        """Estimate remaining budget ratio from X-MBX-USED-WEIGHT-* headers.

        Returns a value in [0, 1] representing how much of the presumed window
        has been consumed (1.0 == at limit). None if not enough info.
        """
        used_min = headers.get("X-MBX-USED-WEIGHT-1m") or headers.get("x-mbx-used-weight-1m")
        used_10s = headers.get("X-MBX-USED-WEIGHT-10S") or headers.get("x-mbx-used-weight-10s")

        ratios: List[float] = []
        if used_min is not None:
            try:
                ratios.append(float(used_min) / float(self._WEIGHT_LIMITS["1m"]))
            except Exception:
                pass
        if used_10s is not None and "10s" in self._WEIGHT_LIMITS:
            try:
                ratios.append(float(used_10s) / float(self._WEIGHT_LIMITS["10s"]))
            except Exception:
                pass
        if ratios:
            # Return the maximum consumption ratio observed among windows
            return max(0.0, min(1.0, max(ratios)))
        return None

    def _binance_rate_limit_hook(self, response) -> Optional[float]:
        """Response hook to parse Binance rate-limit headers and request backoff.

        If consumption ratio crosses 80%, request a gentle delay to spread load
        within the window. If 95%+, be more conservative. This is additive to
        any explicit Retry-After handling in HTTP client for 429/418.
        """
        try:
            headers = dict(response.headers)  # CIMultiDictProxy -> dict[str,str]
            ratio = self._estimate_weight_budget(headers)
            if ratio is None:
                return None
            # Heuristic delays based on ratio; tuned to be small and non-invasive
            if ratio >= 0.95:
                return 1.0  # 1s pause near saturation
            if ratio >= 0.90:
                return 0.5
            if ratio >= 0.80:
                return 0.2
            return None
        except Exception:
            return None

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_candles(
        self,
        symbol: str,
        interval: TimeInterval,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Candle]:
        """Fetch OHLCV candles from Binance."""
        self.validate_symbol(symbol)
        self.validate_interval(interval)

        params: Dict = {
            "symbol": symbol.upper(),
            "interval": self.INTERVAL_MAP[interval],
        }

        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
        if limit:
            max_limit = 1000  # Conservative limit that works for both markets
            params["limit"] = min(limit, max_limit)

        endpoint = self._get_klines_endpoint()
        try:
            data = await self._http.get(endpoint, params=params)
        except Exception as e:
            if "Invalid symbol" in str(e):
                raise InvalidSymbolError(f"Symbol {symbol} not found on Binance")
            raise

        return [self._parse_candle(symbol, candle_data) for candle_data in data]

    def _parse_candle(self, symbol: str, data: List) -> Candle:
        """Parse Binance kline data into Candle model."""
        return Candle(
            symbol=symbol.upper(),
            timestamp=datetime.fromtimestamp(data[0] / 1000),
            open=Decimal(str(data[1])),
            high=Decimal(str(data[2])),
            low=Decimal(str(data[3])),
            close=Decimal(str(data[4])),
            volume=Decimal(str(data[5])),
        )

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_symbols(self, quote_asset: Optional[str] = None, use_cache: bool = True) -> List[Symbol]:
        """Fetch all trading symbols from Binance.
        
        Args:
            quote_asset: Optional filter by quote asset (e.g., "USDT", "BTC")
            use_cache: When True (default), use in-memory cache within TTL
        
        Returns:
            List of Symbol objects. For FUTURES market, returns PERPETUAL contracts only.
        """
        # Serve from cache if fresh
        if use_cache and self._symbols_cache is not None and self._symbols_cache_ts is not None:
            if (time.time() - self._symbols_cache_ts) < self._symbols_cache_ttl:
                if quote_asset:
                    return [s for s in self._symbols_cache if s.quote_asset == quote_asset]
                return list(self._symbols_cache)

        endpoint = self._get_exchange_info_endpoint()
        try:
            data = await self._http.get(endpoint)
        except Exception as e:
            raise Exception(f"Failed to fetch symbols from Binance: {e}")

        # Update rate limit heuristics from exchange info if present
        try:
            for rl in data.get("rateLimits", []) or []:
                if not isinstance(rl, dict):
                    continue
                rl_type = rl.get("rateLimitType") or rl.get("rateLimitType".lower())
                if rl_type not in ("REQUEST_WEIGHT", "RAW_REQUESTS"):
                    continue
                interval = (rl.get("interval") or rl.get("interval".lower()) or "").upper()
                interval_num = rl.get("intervalNum") or rl.get("intervalnum")
                limit = rl.get("limit")
                if limit is None or interval_num is None:
                    continue
                # Map to our keys currently tracked
                key = None
                if interval == "MINUTE" and interval_num == 1:
                    key = "1m"
                elif interval == "SECOND" and interval_num == 10:
                    key = "10s"
                if key:
                    try:
                        self._WEIGHT_LIMITS[key] = int(limit)
                    except Exception:
                        pass
        except Exception:
            # Never let heuristics update break symbols
            pass

        symbols: List[Symbol] = []
        for symbol_data in data.get("symbols", []):
            # Skip non-trading symbols
            if symbol_data.get("status") != "TRADING":
                continue
            
            # Filter by quote asset if specified
            if quote_asset and symbol_data.get("quoteAsset") != quote_asset:
                continue
            
            # For futures, filter for PERPETUAL contracts only
            if self.market_type == MarketType.FUTURES:
                if symbol_data.get("contractType") != "PERPETUAL":
                    continue
            
            # Extract trading filters for metadata
            tick_size = None
            step_size = None
            min_notional = None

            for f in symbol_data.get("filters", []):
                ftype = f.get("filterType") or f.get("filterType".lower())
                if ftype == "PRICE_FILTER":
                    # Futures/Spot both use tickSize
                    val = f.get("tickSize")
                    if val is not None:
                        try:
                            tick_size = Decimal(str(val))
                        except Exception:
                            pass
                elif ftype == "LOT_SIZE":
                    val = f.get("stepSize")
                    if val is not None:
                        try:
                            step_size = Decimal(str(val))
                        except Exception:
                            pass
                elif ftype == "MIN_NOTIONAL":
                    val = f.get("minNotional")
                    if val is not None:
                        try:
                            min_notional = Decimal(str(val))
                        except Exception:
                            pass

            symbols.append(
                Symbol(
                    symbol=symbol_data["symbol"],
                    base_asset=symbol_data["baseAsset"],
                    quote_asset=symbol_data["quoteAsset"],
                    tick_size=tick_size,
                    step_size=step_size,
                    min_notional=min_notional,
                    contract_type=symbol_data.get("contractType"),
                    delivery_date=symbol_data.get("deliveryDate"),
                )
            )
        # Update cache
        self._symbols_cache = symbols
        self._symbols_cache_ts = time.time()

        if quote_asset:
            return [s for s in symbols if s.quote_asset == quote_asset]
        return symbols

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_open_interest(
        self,
        symbol: str,
        historical: bool = False,
        period: str = "5m",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 30,
    ) -> List[OpenInterest]:
        """Fetch Open Interest data from Binance.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            historical: If True, fetch historical OI data; if False, current OI
            period: Time period for historical data (5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d)
            start_time: Start time for historical data
            end_time: End time for historical data  
            limit: Maximum number of records (max 500)
            
        Returns:
            List of OpenInterest objects
            
        Raises:
            InvalidSymbolError: If symbol doesn't exist
            ProviderError: If API request fails
        """
        if self.market_type != MarketType.FUTURES:
            raise ValueError("Open Interest is only available for Futures market")
            
        symbol = symbol.upper()
        
        if historical:
            # Historical OI endpoint
            if period not in OI_PERIOD_MAP:
                raise ValueError(f"Invalid period: {period}. Valid periods: {list(OI_PERIOD_MAP.keys())}")
                
            params = {
                "symbol": symbol,
                "period": OI_PERIOD_MAP[period],
                "limit": min(limit, 500),  # Binance max limit
            }
            
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
                
            try:
                data = await self._http.get("/futures/data/openInterestHist", params=params)
            except Exception as e:
                if "Invalid symbol" in str(e):
                    raise InvalidSymbolError(f"Symbol {symbol} not found on Binance Futures")
                raise
                
            # Historical OI endpoint may return a single dict or list of data points
            if isinstance(data, dict):
                return [self._parse_open_interest_historical(data)]
            else:
                return [self._parse_open_interest_historical(oi_data) for oi_data in data]
        else:
            # Current OI endpoint
            params = {"symbol": symbol}
            try:
                data = await self._http.get("/fapi/v1/openInterest", params=params)
            except Exception as e:
                if "Invalid symbol" in str(e):
                    raise InvalidSymbolError(f"Symbol {symbol} not found on Binance Futures")
                raise
                
            return [self._parse_open_interest_current(data)]

    def _parse_open_interest_current(self, data: Dict) -> OpenInterest:
        """Parse current OI response."""
        from datetime import timezone
        
        return OpenInterest(
            symbol=data["symbol"],
            timestamp=datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc),
            open_interest=Decimal(str(data["openInterest"])),
            # Note: current OI endpoint doesn't provide openInterestValue, calculate from OI * mark price if available
            open_interest_value=None,  # Will be None for current endpoint
        )

    def _parse_open_interest_historical(self, data) -> OpenInterest:
        """Parse historical OI response - handles both dict and array formats."""
        from datetime import timezone
        
        if isinstance(data, dict):
            # Dictionary format (single data point)
            # Note: Historical endpoint may not have timestamp, use current time
            timestamp = datetime.now(timezone.utc)
            if "time" in data:
                timestamp = datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc)
            elif "timestamp" in data:
                timestamp = datetime.fromtimestamp(data["timestamp"] / 1000, tz=timezone.utc)
                
            return OpenInterest(
                symbol=data["symbol"],
                timestamp=timestamp,
                sum_open_interest=Decimal(str(data["sumOpenInterest"])),
                sum_open_interest_value=Decimal(str(data["sumOpenInterestValue"])),
                open_interest=Decimal(str(data["sumOpenInterest"])),  # Use sum as primary
                open_interest_value=Decimal(str(data["sumOpenInterestValue"])),  # Use sum value as primary
            )
        else:
            # Array format (historical data points)
            return OpenInterest(
                symbol=data[0],  # symbol
                timestamp=datetime.fromtimestamp(data[1] / 1000, tz=timezone.utc),  # timestamp
                sum_open_interest=Decimal(str(data[2])),  # sumOpenInterest
                sum_open_interest_value=Decimal(str(data[3])),  # sumOpenInterestValue
                open_interest=Decimal(str(data[2])),  # Use sum as primary
                open_interest_value=Decimal(str(data[3])),  # Use sum value as primary
            )

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_funding_rate(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[FundingRate]:
        """Fetch historical APPLIED funding rate data from Binance.
        
        Returns the actual funding rates that were applied/charged to positions.
        These rates are FIXED for each 8-hour period (00:00, 08:00, 16:00 UTC).
        
        Note: For PREDICTED/NEXT funding rate (changes continuously), use 
        stream_funding_rate() WebSocket method instead.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            start_time: Start time for historical data
            end_time: End time for historical data
            limit: Maximum number of records (default 100, max 1000)
            
        Returns:
            List of FundingRate objects (historical applied rates)
            
        Raises:
            ValueError: If market type is not FUTURES
            InvalidSymbolError: If symbol doesn't exist
            ProviderError: If API request fails
        """
        if self.market_type != MarketType.FUTURES:
            raise ValueError("Funding rate is only available for Futures market")
            
        symbol = symbol.upper()
        
        params = {
            "symbol": symbol,
            "limit": min(limit, 1000),  # Binance max limit
        }
        
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
            
        try:
            data = await self._http.get("/fapi/v1/fundingRate", params=params)
        except Exception as e:
            if "Invalid symbol" in str(e):
                raise InvalidSymbolError(f"Symbol {symbol} not found on Binance Futures")
            raise
            
        # Parse funding rate data
        return [self._parse_funding_rate(fr_data) for fr_data in data]

    def _parse_funding_rate(self, data: Dict) -> FundingRate:
        """Parse funding rate response."""
        from datetime import timezone
        
        return FundingRate(
            symbol=data["symbol"],
            funding_time=datetime.fromtimestamp(data["fundingTime"] / 1000, tz=timezone.utc),
            funding_rate=Decimal(str(data["fundingRate"])),
            mark_price=Decimal(str(data["markPrice"])) if "markPrice" in data else None,
        )

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_order_book(
        self,
        symbol: str,
        limit: int = 100,
    ) -> OrderBook:
        """Fetch current order book (market depth) from Binance.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            limit: Depth limit (5, 10, 20, 50, 100, 500, 1000, 5000)
            
        Returns:
            OrderBook object with bids and asks
            
        Raises:
            InvalidSymbolError: If symbol doesn't exist
            ProviderError: If API request fails
        """
        symbol = symbol.upper()
        
        # Validate limit
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        if limit not in valid_limits:
            # Round to nearest valid limit
            limit = min(valid_limits, key=lambda x: abs(x - limit))
        
        # Endpoint differs by market type
        if self.market_type == MarketType.SPOT:
            endpoint = "/api/v3/depth"
        else:  # FUTURES
            endpoint = "/fapi/v1/depth"
        
        params = {
            "symbol": symbol,
            "limit": limit,
        }
        
        try:
            data = await self._http.get(endpoint, params=params)
        except Exception as e:
            if "Invalid symbol" in str(e):
                raise InvalidSymbolError(f"Symbol {symbol} not found on Binance")
            raise
        
        # Parse order book
        return self._parse_order_book(data, symbol)

    def _parse_order_book(self, data: Dict, symbol: str) -> OrderBook:
        """Parse order book response."""
        from datetime import timezone
        
        # Parse bids and asks
        bids = [(Decimal(str(price)), Decimal(str(qty))) for price, qty in data.get("bids", [])]
        asks = [(Decimal(str(price)), Decimal(str(qty))) for price, qty in data.get("asks", [])]
        
        return OrderBook(
            symbol=symbol,
            last_update_id=data.get("lastUpdateId", 0),
            bids=bids,
            asks=asks,
            timestamp=datetime.now(timezone.utc),
        )

    @retry_async(max_retries=3, base_delay=1.0)
    async def get_recent_trades(
        self,
        symbol: str,
        limit: int = 500,
    ) -> List[Trade]:
        """Fetch recent trades from Binance.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            limit: Number of trades to fetch (max 1000)
            
        Returns:
            List of Trade objects
            
        Raises:
            InvalidSymbolError: If symbol doesn't exist
            ProviderError: If API request fails
        """
        symbol = symbol.upper()
        
        # Endpoint differs by market type
        if self.market_type == MarketType.SPOT:
            endpoint = "/api/v3/trades"
        else:  # FUTURES
            endpoint = "/fapi/v1/trades"
        
        params = {
            "symbol": symbol,
            "limit": min(limit, 1000),  # Binance max limit
        }
        
        try:
            data = await self._http.get(endpoint, params=params)
        except Exception as e:
            if "Invalid symbol" in str(e):
                raise InvalidSymbolError(f"Symbol {symbol} not found on Binance")
            raise
        
        # Parse trades
        return [self._parse_trade(trade_data, symbol) for trade_data in data]

    def _parse_trade(self, data: Dict, symbol: str) -> Trade:
        """Parse trade response."""
        from datetime import timezone
        
        return Trade(
            symbol=symbol,
            trade_id=data["id"],
            price=Decimal(str(data["price"])),
            quantity=Decimal(str(data["qty"])),
            quote_quantity=Decimal(str(data["quoteQty"])) if "quoteQty" in data else None,
            timestamp=datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc),
            is_buyer_maker=data["isBuyerMaker"],
            is_best_match=data.get("isBestMatch"),
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()

    # ----------------------
    # Products and market caps (Binance bapi)
    # ----------------------

    @dataclass(frozen=True)
    class ProductCap:
        symbol: str
        base_asset: str
        quote_asset: str
        price: Decimal
        circulating_supply: Decimal
        circulating_market_cap: Decimal

        def to_dict(self) -> Dict[str, str]:
            return {
                "symbol": self.symbol,
                "base_asset": self.base_asset,
                "quote_asset": self.quote_asset,
                "price": str(self.price),
                "circulating_supply": str(self.circulating_supply),
                "circulating_market_cap": str(self.circulating_market_cap),
            }

    _BINANCE_PRODUCTS_URL = "https://www.binance.com/bapi/asset/v2/public/asset-service/product/get-products"

    async def _fetch_products_raw(self) -> List[Dict[str, Any]]:
        data = await self._http.get(self._BINANCE_PRODUCTS_URL)
        if isinstance(data, dict):
            items = data.get("data")
            if isinstance(items, list):
                return items
        if isinstance(data, list):
            return data
        return []

    def _products_cache_valid(self) -> bool:
        return (
            self._products_cache is not None
            and self._products_cache_ts is not None
            and (time.time() - self._products_cache_ts) <= self._products_cache_ttl
        )

    async def get_products(self, *, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch Binance products (with TTL cache)."""
        if not force_refresh and self._products_cache_valid():
            return list(self._products_cache or [])
        items = await self._fetch_products_raw()
        self._products_cache = items
        self._products_cache_ts = time.time()
        return list(items)

    async def get_market_caps(
        self,
        *,
        quote: Optional[str] = None,
        min_circulating_supply: Optional[Decimal] = None,
        force_refresh: bool = False,
    ) -> List["BinanceProvider.ProductCap"]:
        items = await self.get_products(force_refresh=force_refresh)
        out: List[BinanceProvider.ProductCap] = []
        for it in items:
            symbol = str(it.get("s") or it.get("symbol") or "").upper()
            base = str(it.get("b") or it.get("baseAsset") or "").upper()
            q = str(it.get("q") or it.get("quoteAsset") or "").upper()
            if not symbol or not base or not q:
                continue
            if quote and q != quote.upper():
                continue
            c_raw = it.get("c")
            cs_raw = it.get("cs")
            if c_raw is None or cs_raw is None:
                continue
            try:
                price = Decimal(str(c_raw))
                circ_supply = Decimal(str(cs_raw))
            except Exception:
                continue
            if min_circulating_supply is not None and circ_supply < min_circulating_supply:
                continue
            mc = price * circ_supply
            out.append(
                BinanceProvider.ProductCap(
                    symbol=symbol,
                    base_asset=base,
                    quote_asset=q,
                    price=price,
                    circulating_supply=circ_supply,
                    circulating_market_cap=mc,
                )
            )
        out.sort(key=lambda x: x.circulating_market_cap, reverse=True)
        return out

    async def get_top_market_caps(
        self,
        n: int = 100,
        *,
        quote: Optional[str] = "USDT",
        min_circulating_supply: Optional[Decimal] = None,
        force_refresh: bool = False,
    ) -> List["BinanceProvider.ProductCap"]:
        items = await self.get_market_caps(
            quote=quote,
            min_circulating_supply=min_circulating_supply,
            force_refresh=force_refresh,
        )
        return items[: max(0, n)]

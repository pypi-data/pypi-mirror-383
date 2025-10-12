"""Base provider abstract class."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .enums import TimeInterval


class BaseProvider(ABC):
    """Abstract base class for all data providers."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._session: Optional[object] = None

    @abstractmethod
    async def get_candles(
        self,
        symbol: str,
        interval: TimeInterval,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """Fetch OHLCV candles for a symbol."""
        pass

    @abstractmethod
    async def get_symbols(self) -> List[dict]:
        """Fetch all available trading symbols."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close provider connections and cleanup resources."""
        pass

    def validate_interval(self, interval: TimeInterval) -> None:
        """Validate if interval is supported by provider. Override if needed."""
        pass

    def validate_symbol(self, symbol: str) -> None:
        """Validate symbol format. Override if needed."""
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")

    async def __aenter__(self) -> "BaseProvider":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()

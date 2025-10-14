import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from pydantic import ConfigDict

from sirius.common import DataClass, Currency


class FinancialInstrument(DataClass):
    name: str
    currency: Currency
    model_config = ConfigDict(frozen=True)


class Stock(FinancialInstrument, ABC):
    ticker: str

    @staticmethod
    @abstractmethod
    async def _find(ticker: str) -> List["Stock"]:
        ...

    @staticmethod
    async def find(ticker: str) -> List["Stock"]:
        from sirius.market_data.ibkr import IBKRStock
        return await IBKRStock._find(ticker)


class Option(FinancialInstrument, ABC):
    underlying_stock: Stock
    strike_price: Decimal
    expiry_date: datetime.date
    type: str

    @staticmethod
    @abstractmethod
    async def _get(abstract_stock: Stock, number_of_days_to_expiry: int) -> List["Option"]:
        ...

    @staticmethod
    async def get(abstract_stock: Stock, number_of_days_to_expiry: int) -> List["Option"]:
        from sirius.market_data.ibkr import IBKROption
        return await IBKROption._get(abstract_stock, number_of_days_to_expiry)


class MarketData(DataClass, ABC):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    timestamp: datetime.datetime
    financial_instrument: FinancialInstrument

    @staticmethod
    @abstractmethod
    async def _get(abstract_stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List["MarketData"]:
        ...

    @staticmethod
    async def get(stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime | None = None) -> List["MarketData"]:
        from sirius.market_data.ibkr import IBKRMarketData
        to_timestamp = datetime.datetime.now() if not to_timestamp else to_timestamp
        return await IBKRMarketData._get(stock, from_timestamp, to_timestamp)

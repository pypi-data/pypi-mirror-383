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
    async def get(stock: Stock, number_of_days_to_expiry: int) -> List["Option"]:
        ...


    @staticmethod
    @abstractmethod
    async def find(ticker: str, number_of_days_to_expiry: int) -> List["Option"]:
        ...


class MarketData(DataClass):
    close: Decimal
    timestamp: datetime.datetime
    contract: FinancialInstrument

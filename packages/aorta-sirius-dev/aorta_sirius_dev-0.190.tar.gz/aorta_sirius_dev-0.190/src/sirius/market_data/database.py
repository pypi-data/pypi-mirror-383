import datetime
from typing import Optional, List, cast

from beanie import DecimalAnnotation, Link

from sirius.common import PersistedDataClass
from sirius.market_data import Stock, StockMarketData, MarketDataException
from sirius.market_data.ibkr import IBKRStockMarketData, IBKRStock


class CachedStock(PersistedDataClass, Stock):  # type:ignore[misc]
    id: str  # type:ignore[assignment]

    @staticmethod
    async def _find(ticker: str) -> Optional["Stock"]:
        cached_stock: CachedStock | None = await CachedStock.find_one(CachedStock.id == ticker)
        if cached_stock:
            return cached_stock

        ibkr_stock: IBKRStock = cast(IBKRStock, await IBKRStock._find(ticker))
        cached_stock = CachedStock(
            id=ibkr_stock.ticker,
            name=ibkr_stock.name,
            ticker=ibkr_stock.ticker,
            currency=ibkr_stock.currency
        )
        return await cached_stock.save()


class CachedStockMarketData(PersistedDataClass, StockMarketData):  # type:ignore[misc]
    id: str  # type:ignore[assignment]
    open: DecimalAnnotation
    high: DecimalAnnotation
    low: DecimalAnnotation
    close: DecimalAnnotation
    stock: Link[CachedStock]  # type:ignore[assignment]

    @staticmethod
    async def _get(abstract_stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List["StockMarketData"]:
        cached_data_list: List[CachedStockMarketData] = await CachedStockMarketData.find(
            CachedStockMarketData.stock.id == abstract_stock.ticker,  # type:ignore[attr-defined]
            CachedStockMarketData.timestamp >= from_timestamp,
            CachedStockMarketData.timestamp <= to_timestamp,
            fetch_links=False,
        ).to_list()
        earliest_data: CachedStockMarketData | None = min(cached_data_list, key=lambda c: c.timestamp) if cached_data_list else None
        latest_data: CachedStockMarketData | None = max(cached_data_list, key=lambda c: c.timestamp) if cached_data_list else None

        if not cached_data_list or (earliest_data.timestamp - from_timestamp).days >= 1 or (to_timestamp - latest_data.timestamp).days >= 1:
            cached_stock: CachedStock = cast(CachedStock, await CachedStock._find(abstract_stock.ticker))
            latest_market_data_list: List[StockMarketData] = await IBKRStockMarketData._get(abstract_stock, from_timestamp, to_timestamp)

            if not cached_stock:
                raise MarketDataException(f"Could not find Cached stock for stock with ticker {abstract_stock.ticker}")

            if len(latest_market_data_list) == 0:
                raise MarketDataException(f"Market data for stock with ticker {abstract_stock.ticker}")

            cached_data_list = [CachedStockMarketData(
                id=f"{market_data.stock.ticker} | {int(market_data.timestamp.timestamp())}",
                open=market_data.open,
                high=market_data.high,
                low=market_data.low,
                close=market_data.close,
                timestamp=market_data.timestamp,
                stock=cached_stock)
                for market_data in latest_market_data_list]
            cached_data_list = list({x.id: x for x in cached_data_list}.values())  # Removes duplicates with respect to the ID

            await CachedStockMarketData.insert_many(cached_data_list)

        return cached_data_list  # type: ignore[return-value]

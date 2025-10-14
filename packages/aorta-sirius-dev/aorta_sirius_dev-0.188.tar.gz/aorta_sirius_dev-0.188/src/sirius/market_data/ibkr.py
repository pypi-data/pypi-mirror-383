import asyncio
import datetime
import itertools
from decimal import Decimal
from typing import List, Dict, Any, cast, Set

from async_lru import alru_cache

from sirius import common
from sirius.common import Currency
from sirius.http_requests import HTTPResponse
from sirius.ibkr import session, base_url, Exchange
from sirius.market_data import Stock, Option

OPTIONS_DATE_FORMAT: str = "%b%y"


class IBKRStock(Stock):
    contract_id: int

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def _find(ticker: str) -> List[Stock]:
        stock_list: List[Stock] = []
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType=STK")
        filtered_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        contract_id_list: List[int] = [int(data["conid"]) for data in filtered_list]

        for contract_id in contract_id_list:
            response = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
            stock_list.append(IBKRStock(
                name=response.data["company_name"],
                currency=Currency(response.data["currency"]),
                ticker=response.data["symbol"],
                contract_id=contract_id
            ))

        return stock_list


class IBKROption(Option):
    contract_id: int

    @staticmethod
    async def _get_all_expiry_month_list(stock: IBKRStock, number_of_days_to_expiry: int | None = None) -> List[datetime.date]:
        number_of_days_to_expiry = 3 if not number_of_days_to_expiry else number_of_days_to_expiry
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={stock.ticker}&secType=STK")
        data: Dict[str, Any] = next(filter(lambda c: int(c["conid"]) == stock.contract_id, response.data))
        option_data: Dict[str, Any] = next(filter(lambda o: o["secType"] == "OPT", data["sections"]))
        all_expiry_month_str_list: List[str] = option_data["months"].split(";")
        all_expiry_month_list: List[datetime.date] = [datetime.datetime.strptime(expiry_month, OPTIONS_DATE_FORMAT).date() for expiry_month in all_expiry_month_str_list]

        return [date for date in all_expiry_month_list if (date - datetime.datetime.now().date()).days <= number_of_days_to_expiry]

    @staticmethod
    async def _get_for_strike_and_expiry(stock: IBKRStock, expiry_month: datetime.date, strike_price: Decimal) -> List["IBKROption"]:
        expiry_month_str: str = expiry_month.strftime(OPTIONS_DATE_FORMAT).upper()
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/secdef/info",
            query_params={
                "conid": stock.contract_id,
                "sectype": "OPT",
                "month": expiry_month_str,
                "strike": float(strike_price)}
        )

        return [IBKROption(
            contract_id=data["conid"],
            strike_price=strike_price,
            expiry_date=datetime.datetime.strptime(data["maturityDate"], '%Y%m%d').date(),
            type="CALL" if data["right"] == "C" else "PUT",
            underlying_stock=stock,
            name=f"{stock.name} | {common.get_decimal_str(strike_price)}",
            currency=stock.currency
        ) for data in response.data]

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def get(abstract_stock: Stock, number_of_days_to_expiry: int) -> List[Option]:
        stock: IBKRStock = cast(IBKRStock, abstract_stock if isinstance(abstract_stock, IBKRStock) else (await IBKRStock.find(abstract_stock.ticker))[0])
        option_contract_list: List[Option] = []
        expiry_month_list: List[datetime.date] = await IBKROption._get_all_expiry_month_list(stock, number_of_days_to_expiry)
        expiry_month_str_list: List[str] = [expiry_month.strftime(OPTIONS_DATE_FORMAT).upper() for expiry_month in expiry_month_list]

        responses: List[HTTPResponse] = await asyncio.gather(*[
            session.get(f"{base_url}iserver/secdef/strikes", query_params={"conid": stock.contract_id, "sectype": "OPT", "month": expiry_month_str})
            for expiry_month_str in expiry_month_str_list
        ])
        for expiry_month, response in zip(expiry_month_list, responses):
            all_strike_price_set: Set[Decimal] = set([Decimal(str(strike_price)) for strike_price in response.data.get("call", [])])
            all_strike_price_set.update([Decimal(str(strike_price)) for strike_price in response.data.get("put", [])])
            all_option_contract_list: List[IBKROption] = list(itertools.chain.from_iterable(await asyncio.gather(*[
                IBKROption._get_for_strike_and_expiry(stock, expiry_month, strike_price)
                for strike_price in all_strike_price_set
            ])))

            option_contract_list.extend(
                [option
                 for option in all_option_contract_list
                 if (option.expiry_date - datetime.datetime.now().date()).days == number_of_days_to_expiry]
            )

        return option_contract_list

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def find(ticker: str, number_of_days_to_expiry: int) -> List["Option"]:
        stock_list: List[IBKRStock] = cast(List[IBKRStock], await IBKRStock.find(ticker))
        return (await asyncio.gather(*[IBKROption.get(stock, number_of_days_to_expiry) for stock in stock_list]))[0]

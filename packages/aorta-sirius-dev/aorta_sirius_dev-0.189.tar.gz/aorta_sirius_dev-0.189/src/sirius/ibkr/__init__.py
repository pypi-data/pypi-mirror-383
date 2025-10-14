import asyncio
import datetime
import itertools
from datetime import timedelta
from decimal import Decimal
from enum import Enum, auto
from typing import List, Dict, Any, Type, Set, Optional, Callable

import httpx
import numpy
from async_lru import alru_cache
from pydantic import ConfigDict
from scipy.stats import norm

from sirius import common
from sirius.common import DataClass, Currency
from sirius.exceptions import OperationNotSupportedException
from sirius.http_requests import AsyncHTTPSession, HTTPResponse, ServerSideException

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()

base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL", "https://ibkr-service:5000/v1/api/")
session: AsyncHTTPSession = AsyncHTTPSession(base_url)
session.client = httpx.AsyncClient(verify=False, timeout=60)
OPTIONS_DATE_FORMAT: str = "%b%y"


def calculate_annualized_return(starting: Decimal, ending: Decimal, number_of_days: int) -> Decimal:
    daily_return = (ending / starting)
    annualization_factor = Decimal("365") / Decimal(number_of_days)
    annualized_return = daily_return ** annualization_factor - Decimal("1")
    return annualized_return


class ContractType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    FUTURE_OPTION = "FOP"
    BOND = "BND"


class OptionContractType(Enum):
    PUT = auto()
    CALL = auto()


class Exchange(Enum):
    NASDAQ = "NASDAQ"


class IBKRAccount(DataClass):
    id: str
    name: str

    @staticmethod
    async def get_all_ibkr_accounts() -> List["IBKRAccount"]:
        global _account_list
        if len(_account_list) == 0:
            async with _account_list_lock:
                if len(_account_list) == 0:
                    response: HTTPResponse = await session.get(f"{base_url}/portfolio/accounts/")
                    _account_list = [IBKRAccount(id=data["id"], name=data["accountAlias"] if data["accountAlias"] else data["id"]) for data in response.data]

        return _account_list




# class ContractPerformance(DataClass):
#     position_open: MarketData
#     position_close: MarketData
#     absolute_return: Decimal
#     annualized_return: Decimal
#
#     @staticmethod
#     def _construct(position_open: MarketData, position_close: MarketData) -> "ContractPerformance":
#         absolute_return: Decimal = (position_close.close - position_open.close) / position_open.close
#         number_of_days = Decimal((position_close.date - position_open.date).days)
#         annualized_return = calculate_annualized_return(position_open.close, position_close.close, int(number_of_days))
#
#         return ContractPerformance(
#             position_open=position_open,
#             position_close=position_close,
#             absolute_return=absolute_return,
#             annualized_return=annualized_return
#         )
#
#     @staticmethod
#     async def get(contract_id: int, position_start_date: datetime.date, number_of_days: int) -> Optional["ContractPerformance"]:
#         position_close_date: datetime.date = position_start_date + timedelta(days=number_of_days)
#         market_data_map: Dict[datetime.date, MarketData] = await MarketData.get(contract_id)
#         position_open = market_data_map.get(position_start_date)
#         position_close = market_data_map.get(position_close_date)
#
#         if not position_open or not position_close:
#             return None
#
#         return ContractPerformance._construct(position_open, position_close)
#
#
# class ContractPerformanceAnalysis(DataClass):
#     contract_performance_list: List[ContractPerformance]
#     standard_deviation_absolute_return: Decimal
#     standard_deviation_annualized_return: Decimal
#     mean_absolute_return: Decimal
#     mean_annualized_return: Decimal
#     median_absolute_return: Decimal
#     median_annualized_return: Decimal
#     min_absolute_return: Decimal
#     min_annualized_return: Decimal
#     max_absolute_return: Decimal
#     max_annualized_return: Decimal
#
#     @staticmethod
#     async def _get_contract_performance_list(contract_id: int, number_of_days_invested: int, number_of_days_to_analyse: int, analysis_end_date: datetime.date) -> List["ContractPerformance"]:
#         analysis_dates_list = [analysis_end_date - datetime.timedelta(days=day) for day in range(number_of_days_to_analyse)]
#         performances_tasks = [ContractPerformance.get(contract_id, date, number_of_days_invested) for date in analysis_dates_list]
#         contract_performance_results = await asyncio.gather(*performances_tasks)
#
#         return [result for result in contract_performance_results if result is not None]
#
#     @staticmethod
#     @alru_cache(maxsize=50, ttl=600)  # 5 min cache
#     async def get(contract_id: int, number_of_days_invested: int, number_of_days_to_analyse: int, analysis_end_date: datetime.date | None = None) -> "ContractPerformanceAnalysis":
#         analysis_end_date = analysis_end_date if analysis_end_date else datetime.datetime.now().date()
#         contract_performance_list: List[ContractPerformance] = await ContractPerformanceAnalysis._get_contract_performance_list(contract_id, number_of_days_invested, number_of_days_to_analyse, analysis_end_date)
#
#         if not contract_performance_list:
#             raise ServerSideException("Did not retrieve any Market Data")
#
#         absolute_return_list: List[Decimal] = [contract_performance.absolute_return for contract_performance in contract_performance_list]
#         annualized_return_list: List[Decimal] = [contract_performance.annualized_return for contract_performance in contract_performance_list]
#         standard_deviation_absolute_return: Decimal = Decimal(str(numpy.std(absolute_return_list)))  # type: ignore[arg-type]
#         standard_deviation_annualized_return: Decimal = Decimal(str(numpy.std(annualized_return_list)))  # type: ignore[arg-type]
#         mean_absolute_return: Decimal = Decimal(str(numpy.mean(absolute_return_list)))  # type: ignore[arg-type]
#         mean_annualized_return: Decimal = Decimal(str(numpy.mean(annualized_return_list)))  # type: ignore[arg-type]
#         median_absolute_return: Decimal = Decimal(str(numpy.median(absolute_return_list)))  # type: ignore[arg-type]
#         median_annualized_return: Decimal = Decimal(str(numpy.median(annualized_return_list)))  # type: ignore[arg-type]
#         min_absolute_return: Decimal = Decimal(str(numpy.min(absolute_return_list)))  # type: ignore[arg-type]
#         min_annualized_return: Decimal = Decimal(str(numpy.min(annualized_return_list)))  # type: ignore[arg-type]
#         max_absolute_return: Decimal = Decimal(str(numpy.max(absolute_return_list)))  # type: ignore[arg-type]
#         max_annualized_return: Decimal = Decimal(str(numpy.max(annualized_return_list)))  # type: ignore[arg-type]
#
#         return ContractPerformanceAnalysis(
#             contract_performance_list=contract_performance_list,
#             standard_deviation_absolute_return=standard_deviation_absolute_return,
#             standard_deviation_annualized_return=standard_deviation_annualized_return,
#             mean_absolute_return=mean_absolute_return,
#             mean_annualized_return=mean_annualized_return,
#             median_absolute_return=median_absolute_return,
#             median_annualized_return=median_annualized_return,
#             min_absolute_return=min_absolute_return,
#             min_annualized_return=min_annualized_return,
#             max_absolute_return=max_absolute_return,
#             max_annualized_return=max_annualized_return
#         )
#
#
# class OptionPerformanceAnalysis(DataClass):
#     option_contract: OptionContract
#     contract_performance_analysis: ContractPerformanceAnalysis
#     itm_probability: Decimal
#
#     @staticmethod
#     async def get(option_contract: OptionContract) -> "OptionPerformanceAnalysis":
#         today: datetime.date = datetime.datetime.now().date()
#         number_of_days_to_analyse: int = (today - today.replace(year=today.year - 10)).days
#         number_of_days_invested: int = (option_contract.expiry_date - datetime.datetime.now().date()).days
#         underlying_price: Decimal = await MarketData.get_latest_price(option_contract.underlying_contract.id)
#         itm_required_absolute_return: Decimal = (option_contract.strike_price - underlying_price) / underlying_price
#         contract_performance_analysis: ContractPerformanceAnalysis = await ContractPerformanceAnalysis.get(option_contract.underlying_contract.id, number_of_days_invested, number_of_days_to_analyse)
#         itm_probability_func: Callable[[], Decimal] = lambda: Decimal(str(norm.cdf(float(itm_required_absolute_return), float(contract_performance_analysis.mean_absolute_return), float(contract_performance_analysis.standard_deviation_absolute_return))))
#         itm_probability: Decimal = itm_probability_func() if option_contract.type == OptionContractType.PUT else Decimal("1") - itm_probability_func()
#
#         return OptionPerformanceAnalysis(
#             option_contract=option_contract,
#             contract_performance_analysis=contract_performance_analysis,
#             itm_probability=itm_probability
#         )

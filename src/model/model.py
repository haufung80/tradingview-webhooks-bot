from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import pytz
from pydantic import validate_arguments
from sqlalchemy import Column, DateTime, func, String, Float, Boolean, REAL
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in dir(self):
                exec(f"self.{key} = {value}")

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now())


class OrderHistory(Base, BaseMixin):
    __tablename__ = 'order_history'

    order_id = Column(String(), unique=True)
    strategy_id = Column(String(50))
    source_symbol = Column(String(20))
    exchange_symbol = Column(String(20))
    action = Column(String(10))
    order_status = Column(String(20))
    order_price = Column(REAL())
    avg_price = Column(REAL())
    exec_value = Column(REAL())
    order_amt = Column(REAL())
    open_timestamp = Column(String(20))
    open_datetime = Column(DateTime(timezone=True))
    fill_timestamp = Column(String(20))
    fill_datetime = Column(DateTime(timezone=True))
    filled_amt = Column(REAL())
    fee_rate = Column(REAL())
    total_fee = Column(REAL())
    active = Column(Boolean())
    position_size = Column(REAL())
    position_fund = Column(Float(20))
    fund_diff = Column(REAL())
    total_fund = Column(Float(20))
    exchange = Column(String(20))
    order_payload_1 = Column(String())
    order_payload_2 = Column(String())


class AlertHistory(Base, BaseMixin):
    __tablename__ = 'alert_history'

    source = Column(String(50))
    message_payload = Column(String())
    strategy_id = Column(String(50))
    timestamp = Column(DateTime(timezone=True))
    symbol = Column(String(50))
    exchange = Column(String(50))
    action = Column(String(50))
    price = Column(Float())
    position_size = Column(String(50))


class Strategy(Base, BaseMixin):
    __tablename__ = 'strategy'

    strategy_id = Column(String(50), unique=True)
    strategy_name = Column(String(50))
    symbol = Column(String(50))
    position_size = Column(Float())
    direction = Column(String(10))
    active = Column(Boolean())
    personal_acc = Column(Boolean())
    backtest_period = Column(String(10))
    sr = Column(Float())
    b_sr = Column(Float())
    win_rate = Column(Float())
    trd_num = Column(INTEGER())
    sim_ret = Column(Float())
    bnh_ret = Column(Float())
    sim_mdd = Column(Float())
    bnh_mdd = Column(Float())
    expos = Column(Float())
    leverage = Column(Float())
    timeframe = Column(String(20))
    is_lev = Column(Boolean())

    def calculate_fund_diff(self, curr_action, closed_price, open_price, total_fee):
        if curr_action == 'sell':
            return closed_price - open_price - total_fee
        else:
            return open_price - closed_price - total_fee


class StrategyManagement(Base, BaseMixin):
    __tablename__ = 'strategy_management'
    strat_mgmt_id = Column(String(100), unique=True)
    strategy_id = Column(String(50))
    active_order = Column(Boolean())
    fund = Column(Float())
    init_fund = Column(Float())
    exchange = Column(String(50))
    active = Column(Boolean())


class OrderExecutionError(Base, BaseMixin):
    __tablename__ = 'order_execution_error'
    alert_id = Column(INTEGER(10))
    error = Column(String())
    error_stack = Column(String())
    exchange = Column(String(20))


class TradingViewAlert:
    def __init__(self, resp):
        self.strategy_id = resp['data']['strategy_id']
        self.action = resp['data']['action']
        self.price = float(resp['data']['price'])
        self.symbol = resp['data']['symbol']
        self.timestamp = resp['data']['timestamp']
        self.exchange = resp['data']['exchange']
        self.source = resp['data']['source']
        self.position_size = resp['data']['position_size']
        self.payload = str(resp['data'])

    id: int
    strategy_id: str
    action: str
    price: float
    symbol: str
    timestamp: str
    exchange: str
    source: str
    position_size: str
    payload: str

    def get_date(self):
        return pytz.timezone('UTC').localize(
            datetime.strptime(self.timestamp, '%Y-%m-%dT%H:%M:%SZ'))


@validate_arguments
@dataclass
class BybitOrderResponse:
    def __init__(self, resp):
        self.id = resp['id']
        self.payload = str(resp)

    id: str
    payload: str


@validate_arguments
@dataclass
class BitgetOrderResponse:
    def __init__(self, resp):
        self.id = resp['id']
        self.payload = str(resp)

    id: str
    payload: str


@validate_arguments
@dataclass
class OkexOrderResponse:
    def __init__(self, resp):
        self.id = resp['id']
        self.payload = str(resp)

    id: str
    payload: str


class CryptoExchange(Enum):
    BYBIT = 'BYBIT'
    # BITGET = 'BITGET'
    # OKEX = 'OKEX'


class ExchangeOrderStatus(Enum):
    BYBIT_NEW = 'New'
    BYBIT_PARTIALLY_FILLED = 'PartiallyFilled'
    BYBIT_FILLED = 'Filled'
    BYBIT_CANCELLED = 'Cancelled'
    # BITGET_NEW = 'open'
    # BITGET_PARTIALLY_FILLED = 'partiallyfilled'
    # BITGET_FILLED = 'filled'
    # BITGET_SPOT_FILLED = 'full_fill'
    # BITGET_CANCELLED = 'canceled'
    # OKEX_NEW = 'live'
    # OKEX_PARTIALLY_FILLED = 'partially_filled'
    # OKEX_FILLED = 'filled'
    # OKEX_CANCELLED = 'canceled'


class FetchOrderResponse:
    order_status: str
    created_time: int
    payload: str

    avg_price: float
    cum_exec_value: float
    updated_time: int
    filled: float
    _cum_exec_fee: float

    def get_open_datetime(self):
        return datetime.fromtimestamp(self.created_time / 1000, pytz.timezone('Asia/Nicosia'))

    def get_fill_datetime(self):
        return datetime.fromtimestamp(self.updated_time / 1000, pytz.timezone('Asia/Nicosia'))

    def get_fee_rate(self):
        return abs(self._cum_exec_fee / self.cum_exec_value)

    def get_total_fee(self):
        return abs(self._cum_exec_fee)


class BybitFetchOrderResponse(FetchOrderResponse):
    def __init__(self, resp):
        self.order_status = resp['info']['orderStatus']
        self.created_time = int(resp['info']['createdTime'])
        self.payload = str(resp)

        self.updated_time = int(resp['info']['updatedTime'])
        self.avg_price = 0  # assume avg_price is 0
        if self.order_status == ExchangeOrderStatus.BYBIT_FILLED.value or self.order_status == ExchangeOrderStatus.BYBIT_PARTIALLY_FILLED.value:
            self.avg_price = float(resp['info']['avgPrice'])
        self.cum_exec_value = float(resp['info']['cumExecValue'])
        self._cum_exec_fee = float(resp['info']['cumExecFee'])
        if ':USDT' in resp['symbol'] or (':USDT' not in resp['symbol'] and resp[
            'side'] == 'sell'):  # meaning it is contract or selling spot order
            self.filled = float(resp['filled'])
            self.cum_exec_value = float(resp['info']['cumExecValue'])
            self._cum_exec_fee = float(resp['info']['cumExecFee'])
        else:  # buying spot logic
            self.cum_exec_value = float(resp['info']['cumExecValue'])
            self._cum_exec_fee = float(
                resp['info']['cumExecFee']) * self.avg_price  # cumExecFee is the number in the coins you buy
            self.filled = float(resp['filled']) - float(resp['info']['cumExecFee'])


# class BitgetFetchOrderResponse(FetchOrderResponse):
#     def __init__(self, resp):
#         self.created_time = resp['timestamp']
#         self.payload = str(resp)
#
#         self.cum_exec_value = resp['cost']
#         if resp['average'] is not None:
#             self.avg_price = resp['average']
#         else:
#             self.avg_price = 0.0  # just to avoid err, dunno what happen
#
#         self.order_status = resp['status']
#         if self.order_status == 'closed':  # closed status imply it is filled/full_filled/partially_filled
#             if 'state' in resp['info'].keys():
#                 self.order_status = resp['info']['state']  # contract order status is here
#             else:
#                 self.order_status = resp['info']['status']  # spot order status is here
#
#         if resp['side'] == 'buy' and resp['status'] == 'closed' and resp['fee'][
#             'currency'] != 'USDT':  # when buying spot and it is filled, fee is calculated in the coin you buy, '_SPBL' is the copy trade pair
#             fee_detail = json.loads(resp['info']['feeDetail'])
#             self.filled = resp['filled'] - abs(float(fee_detail['newFees']['r']))
#             self._cum_exec_fee = abs(float(fee_detail['newFees']['r'])) * self.avg_price
#             self.updated_time = resp['timestamp']
#         else:
#             if self.order_status == ExchangeOrderStatus.BITGET_SPOT_FILLED.value or \
#                     self.order_status == ExchangeOrderStatus.BITGET_PARTIALLY_FILLED.value or \
#                     self.order_status == ExchangeOrderStatus.BITGET_FILLED.value:
#                 self._cum_exec_fee = resp['fee']['cost']
#             else:
#                 self._cum_exec_fee = 0
#             self.filled = resp['filled']
#             self.updated_time = resp['lastUpdateTimestamp']
#
#
# class OkexFetchOrderResponse(FetchOrderResponse):
#     def __init__(self, resp):
#         self.order_status = resp['info']['state']
#         self.created_time = resp['timestamp']
#         self.payload = str(resp)
#
#         self.cum_exec_value = resp['cost']
#         self.updated_time = resp['lastUpdateTimestamp']
#         if resp['average'] is not None:
#             self.avg_price = resp['average']
#         if resp['info']['feeCcy'] != 'USDT' \
#                 and resp[
#             'average'] is not None:  # when trading spot fee is calculated in the coin itself. 'average' could be null when it is cancelling order
#             self._cum_exec_fee = abs(float(resp['info']['fee'])) * self.avg_price
#             self.filled = resp['filled'] - abs(float(resp['info']['fee']))
#         else:
#             self._cum_exec_fee = abs(float(resp['info']['fee']))
#             self.filled = resp['filled']
#
#
# class BitgetErrorCode(Enum):
#     ORDER_PRICE_HIGHER_THAN_BID_PRICE = "40815"
#     ORDER_PRICE_LOWER_THAN_BID_PRICE = "40816"
#
#
# class OkexErrorCode(Enum):
#     THE_HIGHEST_PRICE_LIMIT_FOR_BUY_ORDERS = "51136"
#     THE_LOWEST_PRICE_LIMIT_FOR_SELL_ORDERS = "51137"


class StrategyDirection(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    PAIR_LONG = "PAIR_LONG"
    PAIR_SHORT = "PAIR_SHORT"
    BOTH = "BOTH"
    PAIR_BOTH = "PAIR_BOTH"

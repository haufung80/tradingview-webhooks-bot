import json
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


class Strategy(Base, BaseMixin):
    __tablename__ = 'strategy'

    strategy_id = Column(String(50), unique=True)
    strategy_name = Column(String(50))
    symbol = Column(String(50))
    position_size = Column(Float())
    parameter_1 = Column(String(50))
    value_1 = Column(String(50))
    parameter_2 = Column(String(50))
    value_2 = Column(String(50))
    parameter_3 = Column(String(50))
    value_3 = Column(String(50))
    parameter_4 = Column(String(50))
    value_4 = Column(String(50))
    parameter_5 = Column(String(50))
    value_5 = Column(String(50))
    expiry_date = Column(DateTime(timezone=True))
    direction = Column(String(10))
    active = Column(Boolean())
    personal_acc = Column(Boolean())

    def calculate_fund_diff(self, closed_price, open_price, total_fee):
        if self.direction == StrategyDirection.LONG.value:
            return closed_price - open_price - total_fee
        else:
            return open_price - closed_price - total_fee


class StrategyManagement(Base, BaseMixin):
    __tablename__ = 'strategy_management'
    strat_mgmt_id = Column(String(100), unique=True)
    strategy_id = Column(String(50))
    active_order = Column(Boolean())
    fund = Column(Float())
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
        self.payload = str(resp['data'])

    id: int
    strategy_id: str
    action: str
    price: float
    symbol: str
    timestamp: str
    exchange: str
    source: str
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
    BITGET = 'BITGET'
    OKEX = 'OKEX'


class ExchangeOrderStatus(Enum):
    BYBIT_NEW = 'New'
    BYBIT_PARTIALLY_FILLED = 'PartiallyFilled'
    BYBIT_FILLED = 'Filled'
    BYBIT_CANCELLED = 'Cancelled'
    BITGET_NEW = 'new'
    BITGET_PARTIALLY_FILLED = 'partiallyfilled'
    BITGET_FILLED = 'filled'
    BITGET_SPOT_FILLED = 'full_fill'
    BITGET_CANCELLED = 'canceled'
    OKEX_NEW = 'live'
    OKEX_PARTIALLY_FILLED = 'partially_filled'
    OKEX_FILLED = 'filled'
    OKEX_CANCELLED = 'canceled'


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

        self.avg_price = float(resp['info']['avgPrice'])
        self.cum_exec_value = float(resp['info']['cumExecValue'])
        self.updated_time = int(resp['info']['updatedTime'])
        self.filled = float(resp['filled'])
        self._cum_exec_fee = float(resp['info']['cumExecFee'])


class BitgetFetchOrderResponse(FetchOrderResponse):
    def __init__(self, resp):
        self.created_time = resp['timestamp']
        self.payload = str(resp)

        self.cum_exec_value = resp['cost']
        if resp['average'] is not None:
            self.avg_price = resp['average']
        else:
            self.avg_price = 0.0  # just to aviod err, dunno what happen
        if '_SPBL' in resp['info']['symbol']:
            self.order_status = resp['info']['status']
            fee_detail = json.loads(resp['info']['feeDetail'])
            self.filled = resp['filled'] - abs(float(fee_detail['newFees']['r']))
            self._cum_exec_fee = abs(float(fee_detail['newFees']['r'])) * self.avg_price
            self.updated_time = resp['timestamp']

        else:
            self.order_status = resp['info']['state']
            self._cum_exec_fee = resp['fee']['cost']
            self.filled = resp['filled']
            self.updated_time = resp['lastUpdateTimestamp']


class OkexFetchOrderResponse(FetchOrderResponse):
    def __init__(self, resp):
        self.order_status = resp['info']['state']
        self.created_time = resp['timestamp']
        self.payload = str(resp)

        self.cum_exec_value = resp['cost']
        self.updated_time = resp['lastUpdateTimestamp']
        if resp['average'] is not None:
            self.avg_price = resp['average']
        if resp['info']['feeCcy'] != 'USDT' \
                and resp[
            'average'] is not None:  # when trading spot fee is calculated in the coin itself. 'average' could be null when it is cancelling order
            self._cum_exec_fee = abs(float(resp['info']['fee'])) * self.avg_price
            self.filled = resp['filled'] - abs(float(resp['info']['fee']))
        else:
            self._cum_exec_fee = abs(float(resp['info']['fee']))
            self.filled = resp['filled']


class BitgetErrorCode(Enum):
    ORDER_PRICE_HIGHER_THAN_BID_PRICE = "40815"
    ORDER_PRICE_LOWER_THAN_BID_PRICE = "40816"


class OkexErrorCode(Enum):
    THE_HIGHEST_PRICE_LIMIT_FOR_BUY_ORDERS = "51136"
    THE_LOWEST_PRICE_LIMIT_FOR_SELL_ORDERS = "51137"


class StrategyDirection(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

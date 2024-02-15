from dataclasses import dataclass
from datetime import datetime

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


class StrategyManagement(Base, BaseMixin):
    __tablename__ = 'strategy_management'
    strategy_id = Column(String(50), unique=True)
    active_order = Column(Boolean())
    fund = Column(Float())


class OrderExecutionError(Base, BaseMixin):
    __tablename__ = 'order_execution_error'
    alert_id = Column(INTEGER(10))
    error = Column(String())
    error_stack = Column(String())


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


class BybitFetchOrderResponse:
    def __init__(self, resp):
        self.order_status = resp['info']['orderStatus']
        self.created_time = resp['info']['createdTime']
        self.payload = str(resp)

        self.avg_price = float(resp['info']['avgPrice'])
        self.cum_exec_value = float(resp['info']['cumExecValue'])
        self.updated_time = resp['info']['updatedTime']
        self.filled = float(resp['filled'])
        self.cum_exec_fee = float(resp['info']['cumExecFee'])

    order_status: str
    created_time: str
    payload: str

    avg_price: float
    cum_exec_value: float
    updated_time: str
    filled: float
    cum_exec_fee: float

    def get_open_datetime(self):
        return datetime.fromtimestamp(int(self.created_time) / 1000, pytz.timezone('Asia/Nicosia'))

    def get_fill_datetime(self):
        return datetime.fromtimestamp(int(self.updated_time) / 1000, pytz.timezone('Asia/Nicosia'))

    def get_fee_rate(self):
        return self.cum_exec_fee / self.cum_exec_value

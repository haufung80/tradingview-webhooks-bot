from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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


@validate_arguments
@dataclass
class TradingViewAlert:
    strategy_id: str
    action: str
    position_size: float
    price: float
    symbol: str
    timestamp: str
    exchange: str
    source: str
    noofcontracts: float
    orderid: str
    comment: str
    alert_msg: str
    market_position: str
    market_position_size: float
    prev_market_position: str
    prev_market_position_size: float

    def get_date(self):
        return pytz.timezone('UTC').localize(
            datetime.strptime(self.timestamp, '%Y-%m-%dT%H:%M:%SZ'))


@validate_arguments
@dataclass
class BybitOrderResponse:
    def __init__(self, resp):
        self.id = resp['id']

    id: str
    payload: Optional[str] = None

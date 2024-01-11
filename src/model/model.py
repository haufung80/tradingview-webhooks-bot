from sqlalchemy import Column, DateTime, func
from sqlalchemy import String, Float, Boolean
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

    order_id = Column(String())
    strategy_id = Column(String(50))
    exec_time = Column(DateTime())
    source_symbol = Column(String(10))
    exchange_symbol = Column(String(10))
    action = Column(String(10))
    order_status = Column(String(10))
    order_price = Column(Float(20))
    avg_price = Column(Float(20))
    exec_value = Column(Float(20))
    order_amt = Column(Float(20))
    open_timestamp = Column(String(20))
    open_datetime = Column(DateTime())
    fill_timestamp = Column(String(20))
    fill_datetime = Column(DateTime())
    filled_amt = Column(Float(20))
    fee_rate = Column(Float(20))
    total_fee = Column(Float(20))
    active = Column(Boolean())
    position_size = Column(Float(10))
    position_fund = Column(Float(20))
    fund_diff = Column(Float(20))
    total_fund = Column(Float(20))
    exchange = Column(String(20))
    order_payload_1 = Column(String())
    order_payload_2 = Column(String())


class AlertHistory(Base, BaseMixin):
    __tablename__ = 'alert_history'

    source = Column(String(50))
    message_payload = Column(String())
    strategy_id = Column(String(50))
    timestamp = Column(DateTime())
    symbol = Column(String(50))
    exchange = Column(String(50))
    action = Column(String(50))
    price = Column(Float())

class Strategy(Base, BaseMixin):
    __tablename__ = 'strategy'

    strategy_id = Column(String(50))
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
    active_order = Column(Boolean())
    fund = Column(Float())

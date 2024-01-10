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

    order_id = Column(String(100))
    strategy_id = Column(String(50))
    execution_time = Column(DateTime())
    symbol = Column(String(50))
    action = Column(String(50))
    price = Column(Float())
    amount = Column(Float())
    active = Column(Boolean())
    fund = Column(Float())
    exchange = Column(String(50))
    order_payload = Column(String())


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

import configparser
import os
import sys
from datetime import datetime

import ccxt as ccxt
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from components.actions.base.action import Action

sys.path.append(os.path.split(os.getcwd())[0])

load_dotenv()
engine = create_engine(os.getenv('POSTGRESQL_URL'), echo=True)

from src.model.model import *


class BybitOrderExecute(Action):
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['BybitSettings']['key']
    API_SECRET = config['BybitSettings']['secret']
    exchange = ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET
    })

    exchange.set_sandbox_mode(config['BybitSettings']['set_sandbox_mode'])

    def __init__(self):
        super().__init__()
        self.exchange.check_required_credentials()  # raises AuthenticationError
        markets = self.exchange.load_markets()

    def place_order(self, data):
        exchange_symbol = None
        if data['symbol'] == 'BTCUSDT.P':
            exchange_symbol = 'BTCUSDT'
        elif data['symbol'] == 'BNBUSDT.P':
            exchange_symbol = 'BNBUSDT'

        with Session(engine) as session:
            session.add(AlertHistory(
                source=data['source'],
                message_payload=str(data),
                strategy_id=data['strategy_id'],
                timestamp=datetime.fromtimestamp(data['timestamp']),
                symbol=data['symbol'],
                exchange=data['exchange'],
                action=data['action'],
                price=data['price'],
            ))
            session.commit()

        with Session(engine) as session:
            strategy = session.execute(select(Strategy).where(Strategy.strategy_id == data['strategy_id'])).scalar_one()
            if data['action'] == 'buy' and not strategy.active_order:
                amount = (strategy.fund * strategy.position_size) / float(data['price'])
                formatted_amount = self.exchange.amount_to_precision(exchange_symbol, amount)
                order = self.exchange.create_limit_order(exchange_symbol, data['action'], formatted_amount,
                                                         data['price'])
                session.add(OrderHistory(
                    order_id=order['info']['orderId'],
                    strategy_id=data['strategy_id'],
                    exec_time=datetime.now(),
                    source_symbol=data['symbol'],
                    exchange_symbol=exchange_symbol,
                    action=data['action'],
                    order_price=data['price'],
                    order_amt=formatted_amount,
                    active=True,
                    position_size=float(data['price']) * float(formatted_amount) / strategy.fund,
                    position_fund=float(data['price']) * float(formatted_amount),
                    total_fund=strategy.fund,
                    exchange=data['exchange'],
                    order_payload_1=str(order)
                ))

                strategy.active_order = True
                session.commit()
            else:
                existing_order_hist = session.execute(select(OrderHistory)
                                                      .where(OrderHistory.strategy_id == data['strategy_id'])
                                                      .where(OrderHistory.exchange == data['exchange'])
                                                      .order_by(OrderHistory.created_at.desc()).limit(1)).scalar_one()
                if existing_order_hist.active:
                    existing_pos_order = self.exchange.fetch_order(existing_order_hist.order_id, exchange_symbol)

                    existing_order_hist.order_status = existing_pos_order['info']['orderStatus']
                    existing_order_hist.avg_price = float(existing_pos_order['info']['avgPrice'])
                    existing_order_hist.exec_value = float(existing_pos_order['info']['cumExecValue'])
                    existing_order_hist.open_timestamp = existing_pos_order['info']['createdTime']
                    existing_order_hist.open_datetime = datetime.fromtimestamp(
                        int(existing_pos_order['info']['createdTime']) / 1000)
                    existing_order_hist.fill_timestamp = existing_pos_order['info']['updatedTime']
                    existing_order_hist.fill_datetime = datetime.fromtimestamp(
                        int(existing_pos_order['info']['updatedTime']) / 1000)
                    existing_order_hist.filled_amt = float(existing_pos_order['filled'])
                    existing_order_hist.fee_rate = float(
                        existing_pos_order['info']['cumExecFee']) / existing_order_hist.exec_value
                    existing_order_hist.total_fee = float(existing_pos_order['info']['cumExecFee'])
                    existing_order_hist.order_payload_2 = str(existing_pos_order)
                    existing_order_hist.fund_diff = -float(existing_pos_order['info']['cumExecFee'])
                    existing_order_hist.total_fund = existing_order_hist.total_fund - float(
                        existing_pos_order['info']['cumExecFee'])
                    existing_order_hist.updated_at = datetime.now()
                    session.flush()

                    order_1 = self.exchange.create_market_order(exchange_symbol, data['action'],
                                                                existing_order_hist.filled_amt)
                    order_2 = self.exchange.fetch_order(order_1['info']['orderId'], exchange_symbol)

                    fund_diff = float(order_2['info']['cumExecValue']) - existing_order_hist.exec_value - float(
                        order_2['info']['cumExecFee'])
                    total_fund = existing_order_hist.total_fund + fund_diff
                    session.add(OrderHistory(
                        order_id=order_1['info']['orderId'],
                        strategy_id=data['strategy_id'],
                        exec_time=datetime.now(),
                        source_symbol=data['symbol'],
                        exchange_symbol=exchange_symbol,
                        action=data['action'],
                        order_price=data['price'],
                        order_amt=existing_order_hist.filled_amt,
                        active=False,
                        exchange=data['exchange'],
                        order_status=order_2['info']['orderStatus'],
                        avg_price=float(order_2['info']['avgPrice']),
                        exec_value=float(order_2['info']['cumExecValue']),
                        open_timestamp=order_2['info']['createdTime'],
                        open_datetime=datetime.fromtimestamp(int(order_2['info']['createdTime']) / 1000),
                        fill_timestamp=order_2['info']['updatedTime'],
                        fill_datetime=datetime.fromtimestamp(int(order_2['info']['updatedTime']) / 1000),
                        filled_amt=float(order_2['filled']),
                        fee_rate=float(order_2['info']['cumExecFee']) / float(order_2['info']['cumExecValue']),
                        total_fee=float(order_2['info']['cumExecFee']),
                        fund_diff=fund_diff,
                        total_fund=total_fund,
                        order_payload_1=str(order_1),
                        order_payload_2=str(order_2),
                    ))

                    strategy.active_order = False
                    strategy.fund = total_fund
                    strategy.updated_at = datetime.now()
                    session.commit()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.place_order(data['data'])

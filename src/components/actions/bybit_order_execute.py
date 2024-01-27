import configparser
import os
import sys
from datetime import datetime

import ccxt as ccxt
import pytz
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from components.actions.base.action import Action

sys.path.append(os.path.split(os.getcwd())[0])

load_dotenv()
engine = create_engine(os.getenv('POSTGRESQL_URL'), echo=True)

from src.model.model import *


def symbol_translate(symbol):
    if symbol == 'BTCUSDT.P':
        return 'BTCUSDT'
    elif symbol == 'SOLUSDT.P':
        return 'SOLUSDT'
    elif symbol == 'CAKEUSDT.P':
        return 'CAKEUSDT'
    elif symbol == 'AVAXUSDT.P':
        return 'AVAXUSDT'
    elif symbol == 'MATICUSDT.P':
        return 'MATICUSDT'
    elif symbol == 'BNBUSDT.P':
        return 'BNBUSDT'
    elif symbol == 'EGLDUSDT.P':
        return 'EGLDUSDT'


def add_alert_history(data):
    with Session(engine) as session:
        session.add(AlertHistory(
            source=data['source'],
            message_payload=str(data),
            strategy_id=data['strategy_id'],
            timestamp=pytz.timezone('UTC').localize(datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')),
            symbol=data['symbol'],
            exchange=data['exchange'],
            action=data['action'],
            price=data['price'],
        ))
        session.commit()


def add_limit_order_history(session, strategy, exchange_symbol, order, formatted_amount, data):
    session.add(OrderHistory(
        order_id=order['info']['orderId'],
        strategy_id=data['strategy_id'],
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
    session.commit()


def add_market_order_history(session, opn_mkt_odr, cls_mkt_odr, exchange_symbol, fund_diff, total_fund, filled_amt,
                             data):
    session.add(OrderHistory(
        order_id=opn_mkt_odr['info']['orderId'],
        strategy_id=data['strategy_id'],
        source_symbol=data['symbol'],
        exchange_symbol=exchange_symbol,
        action=data['action'],
        order_price=data['price'],
        order_amt=filled_amt,
        active=False,
        exchange=data['exchange'],
        order_status=cls_mkt_odr['info']['orderStatus'],
        avg_price=float(cls_mkt_odr['info']['avgPrice']),
        exec_value=float(cls_mkt_odr['info']['cumExecValue']),
        open_timestamp=cls_mkt_odr['info']['createdTime'],
        open_datetime=datetime.fromtimestamp(int(cls_mkt_odr['info']['createdTime']) / 1000,
                                             pytz.timezone('Asia/Nicosia')),
        fill_timestamp=cls_mkt_odr['info']['updatedTime'],
        fill_datetime=datetime.fromtimestamp(int(cls_mkt_odr['info']['updatedTime']) / 1000,
                                             pytz.timezone('Asia/Nicosia')),
        filled_amt=float(cls_mkt_odr['filled']),
        fee_rate=float(cls_mkt_odr['info']['cumExecFee']) / float(cls_mkt_odr['info']['cumExecValue']),
        total_fee=float(cls_mkt_odr['info']['cumExecFee']),
        fund_diff=fund_diff,
        total_fund=total_fund,
        order_payload_1=str(opn_mkt_odr),
        order_payload_2=str(cls_mkt_odr),
    ))
    session.commit()


class BybitOrderExecute(Action):
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['BybitSettings']['key']
    API_SECRET = config['BybitSettings']['secret']
    exchange = ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET
    })

    if config['BybitSettings']['set_sandbox_mode'] == 'True':
        exchange.set_sandbox_mode(True)

    def __init__(self):
        super().__init__()
        self.exchange.check_required_credentials()  # raises AuthenticationError
        markets = self.exchange.load_markets()

    def send_limit_order(self, strategy, exchange_symbol, data):
        amount = (strategy.fund * strategy.position_size) / float(data['price'])
        formatted_amount = self.exchange.amount_to_precision(exchange_symbol, amount)
        order = self.exchange.create_limit_order(exchange_symbol, data['action'], formatted_amount,
                                                 data['price'])
        return order, formatted_amount

    def place_order(self, data):
        add_alert_history(data)
        with Session(engine) as session:
            strategy = session.execute(select(Strategy).where(Strategy.strategy_id == data['strategy_id'])).scalar_one()
            if strategy.active:
                exchange_symbol = symbol_translate(data['symbol'])
                if data['action'] == 'buy' and not strategy.active_order:
                    exc_order_rec, formatted_amount = self.send_limit_order(strategy, exchange_symbol, data)
                    add_limit_order_history(session, strategy, exchange_symbol, exc_order_rec, formatted_amount, data)
                    strategy.active_order = True
                    session.commit()
                elif data['action'] == 'sell' and strategy.active_order:
                    existing_order_hist = session.execute(select(OrderHistory)
                                                          .where(OrderHistory.strategy_id == data['strategy_id'])
                                                          .where(OrderHistory.exchange == data['exchange'])
                                                          .order_by(OrderHistory.created_at.desc()).limit(
                        1)).scalar_one()
                    if existing_order_hist.active:
                        existing_pos_order = self.exchange.fetch_order(existing_order_hist.order_id, exchange_symbol)

                        existing_order_hist.order_status = existing_pos_order['info']['orderStatus']
                        existing_order_hist.open_timestamp = existing_pos_order['info']['createdTime']
                        existing_order_hist.open_datetime = datetime.fromtimestamp(
                            int(existing_pos_order['info']['createdTime']) / 1000, pytz.timezone('Asia/Nicosia'))
                        existing_order_hist.order_payload_2 = str(existing_pos_order)

                        if existing_pos_order['info']['orderStatus'] != 'New':
                            existing_order_hist.avg_price = float(existing_pos_order['info']['avgPrice'])
                            existing_order_hist.exec_value = float(existing_pos_order['info']['cumExecValue'])
                            existing_order_hist.fill_timestamp = existing_pos_order['info']['updatedTime']
                            existing_order_hist.fill_datetime = datetime.fromtimestamp(
                                int(existing_pos_order['info']['updatedTime']) / 1000, pytz.timezone('Asia/Nicosia'))
                            existing_order_hist.filled_amt = float(existing_pos_order['filled'])
                            existing_order_hist.fee_rate = float(
                                existing_pos_order['info']['cumExecFee']) / existing_order_hist.exec_value
                            existing_order_hist.total_fee = float(existing_pos_order['info']['cumExecFee'])
                            existing_order_hist.fund_diff = -float(existing_pos_order['info']['cumExecFee'])

                            existing_order_hist.total_fund = existing_order_hist.total_fund - float(
                                existing_pos_order['info']['cumExecFee'])
                        session.flush()

                        if existing_pos_order['info']['orderStatus'] == 'New' or existing_pos_order['info'][
                            'orderStatus'] == 'PartiallyFilled':
                            order_1 = self.exchange.cancel_order(existing_order_hist.order_id, exchange_symbol)
                            order_2 = self.exchange.fetch_order(order_1['info']['orderId'], exchange_symbol)
                            existing_order_hist.order_payload_2 = str(order_2)  # overriding above
                            existing_order_hist.order_status = order_2['info']['orderStatus']
                            existing_order_hist.active = False

                        if existing_pos_order['info']['orderStatus'] == 'Filled' or existing_pos_order['info'][
                            'orderStatus'] == 'PartiallyFilled':
                            open_mkt_order = self.exchange.create_market_order(exchange_symbol, data['action'],
                                                                               existing_order_hist.filled_amt)
                            closed_mkt_order = self.exchange.fetch_order(open_mkt_order['info']['orderId'],
                                                                         exchange_symbol)
                            fund_diff = float(
                                closed_mkt_order['info']['cumExecValue']) - existing_order_hist.exec_value - float(
                                closed_mkt_order['info']['cumExecFee'])
                            total_fund = existing_order_hist.total_fund + fund_diff
                            add_market_order_history(session, open_mkt_order, closed_mkt_order, exchange_symbol,
                                                     fund_diff,
                                                     total_fund, existing_order_hist.filled_amt,
                                                     data)
                            strategy.fund = total_fund

                        strategy.active_order = False
                        session.commit()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.place_order(data['data'])

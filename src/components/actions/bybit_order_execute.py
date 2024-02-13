import configparser
import json
import os
import sys
import traceback

import ccxt as ccxt
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from components.actions.base.action import Action

sys.path.append(os.path.split(os.getcwd())[0])

load_dotenv()
engine = create_engine(os.getenv('POSTGRESQL_URL'), echo=True)

from src.model.model import *


def symbol_translate(symbol):
    if symbol == 'WEMIXUSDT':
        return 'WEMIXUSDT'
    elif symbol == 'WBTCUSDT':
        return 'WBTCUSDT'
    elif symbol == 'CAKEUSDT':
        return 'CAKEUSDT'
    else:
        return symbol.replace('USDT.P', 'USDT')


def add_alert_history(alert: TradingViewAlert, payload):
    with Session(engine) as session:
        ah = AlertHistory(
            source=alert.source,
            message_payload=payload,
            strategy_id=alert.strategy_id,
            timestamp=alert.get_date(),
            symbol=alert.symbol,
            exchange=alert.exchange,
            action=alert.action,
            price=alert.price
        )
        session.add(ah)
        session.commit()
        return ah.id

def add_limit_order_history(session, strategy_mgmt, exchange_symbol, order, formatted_amount, alrt: TradingViewAlert):
    session.add(OrderHistory(
        order_id=order['info']['orderId'],
        strategy_id=alrt.strategy_id,
        source_symbol=alrt.symbol,
        exchange_symbol=exchange_symbol,
        action=alrt.action,
        order_price=alrt.price,
        order_amt=formatted_amount,
        active=True,
        position_size=alrt.price * float(formatted_amount) / strategy_mgmt.fund,
        position_fund=alrt.price * float(formatted_amount),
        total_fund=strategy_mgmt.fund,
        exchange=alrt.exchange,
        order_payload_1=str(order)
    ))
    session.commit()


def add_market_order_history(session, opn_mkt_odr, cls_mkt_odr, exchange_symbol, fund_diff, total_fund, filled_amt,
                             alrt: TradingViewAlert):
    session.add(OrderHistory(
        order_id=opn_mkt_odr['info']['orderId'],
        strategy_id=alrt.strategy_id,
        source_symbol=alrt.symbol,
        exchange_symbol=exchange_symbol,
        action=alrt.action,
        order_price=alrt.price,
        order_amt=filled_amt,
        active=False,
        exchange=alrt.exchange,
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


def is_duplicate_alert(alert: TradingViewAlert):
    with Session(engine) as session:
        return len(session.execute(
            select(AlertHistory).where(
                AlertHistory.timestamp == alert.get_date(),
                AlertHistory.strategy_id == alert.strategy_id,
                AlertHistory.action == alert.action)
        ).all()) > 0


class BybitOrderExecute(Action):
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['BybitSettings']['key']
    API_SECRET = config['BybitSettings']['secret']
    bybit_exchange = ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET
    })

    API_KEY_PERSONAL = config['BybitSettings']['key_personal']
    API_SECRET_PERSONAL = config['BybitSettings']['secret_personal']
    bybit_exchange_per = ccxt.bybit({
        'apiKey': API_KEY_PERSONAL,
        'secret': API_SECRET_PERSONAL
    })

    if config['BybitSettings']['set_sandbox_mode'] == 'True':
        bybit_exchange.set_sandbox_mode(True)
        bybit_exchange_per.set_sandbox_mode(True)

    def __init__(self):
        super().__init__()
        self.bybit_exchange.check_required_credentials()  # raises AuthenticationError
        self.bybit_exchange_per.check_required_credentials()  # raises AuthenticationError
        markets = self.bybit_exchange.load_markets()
        markets1 = self.bybit_exchange_per.load_markets()

    def send_limit_order(self, strategy, strategy_mgmt, exchange_symbol, alrt: TradingViewAlert, exchange):
        amount = (strategy_mgmt.fund * strategy.position_size) / alrt.price
        if exchange_symbol == 'BTCUSDT' and amount < 0.001:
            formatted_amount = 0.001
        elif exchange_symbol == 'ETHUSDT' and amount < 0.01:
            formatted_amount = 0.01
        else:
            formatted_amount = exchange.amount_to_precision(exchange_symbol, amount)
        order = exchange.create_limit_order(exchange_symbol, alrt.action, formatted_amount,
                                            alrt.price)
        return order, formatted_amount

    def place_order(self, tv_alrt):
        with Session(engine) as session:
            [(strategy, strategy_mgmt)] = session.execute(
                select(Strategy, StrategyManagement).join(StrategyManagement,
                                                          StrategyManagement.strategy_id == Strategy.strategy_id).where(
                    Strategy.strategy_id == tv_alrt.strategy_id)).all()
            if strategy.active:
                if strategy.personal_acc:
                    exchange = self.bybit_exchange_per
                else:
                    exchange = self.bybit_exchange
                exchange_symbol = symbol_translate(tv_alrt.symbol)
                if ((strategy.direction == 'long' and tv_alrt.action == 'buy') or (
                        strategy.direction == 'short' and tv_alrt.action == 'sell')) and not strategy_mgmt.active_order:
                    exc_order_rec, formatted_amount = self.send_limit_order(strategy, strategy_mgmt, exchange_symbol,
                                                                            tv_alrt, exchange)
                    add_limit_order_history(session, strategy_mgmt, exchange_symbol, exc_order_rec, formatted_amount,
                                            tv_alrt)
                    strategy_mgmt.active_order = True
                    session.commit()
                elif ((strategy.direction == 'long' and tv_alrt.action == 'sell') or (
                        strategy.direction == 'short' and tv_alrt.action == 'buy')) and strategy_mgmt.active_order:
                    existing_order_hist = session.execute(select(OrderHistory)
                        .where(OrderHistory.strategy_id == tv_alrt.strategy_id)
                        .where(OrderHistory.exchange == tv_alrt.exchange)
                        .order_by(OrderHistory.created_at.desc()).limit(
                        1)).scalar_one()
                    if existing_order_hist.active:
                        existing_pos_order = exchange.fetch_order(existing_order_hist.order_id, exchange_symbol)

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
                            order_1 = exchange.cancel_order(existing_order_hist.order_id, exchange_symbol)
                            order_2 = exchange.fetch_order(order_1['info']['orderId'], exchange_symbol)
                            existing_order_hist.order_payload_2 = str(order_2)  # overriding above
                            existing_order_hist.order_status = order_2['info']['orderStatus']
                            existing_order_hist.active = False

                        if existing_pos_order['info']['orderStatus'] == 'Filled' or existing_pos_order['info'][
                            'orderStatus'] == 'PartiallyFilled':
                            open_mkt_order = exchange.create_market_order(exchange_symbol, tv_alrt.action,
                                                                          existing_order_hist.filled_amt)
                            closed_mkt_order = exchange.fetch_order(open_mkt_order['info']['orderId'],
                                                                    exchange_symbol)
                            if strategy.direction == 'long':
                                fund_diff = float(
                                    closed_mkt_order['info']['cumExecValue']) - existing_order_hist.exec_value - float(
                                    closed_mkt_order['info']['cumExecFee'])
                            else:
                                fund_diff = float(
                                    existing_order_hist.exec_value - closed_mkt_order['info']['cumExecValue']) - float(
                                    closed_mkt_order['info']['cumExecFee'])

                            total_fund = existing_order_hist.total_fund + fund_diff
                            add_market_order_history(session, open_mkt_order, closed_mkt_order, exchange_symbol,
                                                     fund_diff,
                                                     total_fund, existing_order_hist.filled_amt,
                                                     tv_alrt)
                            strategy_mgmt.fund = total_fund

                        strategy_mgmt.active_order = False
                        session.commit()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        tv_alrt = TradingViewAlert(**json.loads(json.dumps(data['data'])))
        if is_duplicate_alert(tv_alrt):
            _ = add_alert_history(tv_alrt, str(data))
            return
        alert_id = add_alert_history(tv_alrt, str(data))
        try:
            self.place_order(tv_alrt)
        except Exception as e:
            print(traceback.format_exc())
            with Session(engine) as session:
                session.add(OrderExecutionError(
                    alert_id=alert_id,
                    error=e.args,
                    error_stack=traceback.format_exc()
                ))
                session.commit()

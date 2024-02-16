import configparser
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

from model.model import *


def symbol_translate(symbol):
    if symbol == 'WEMIXUSDT':
        return 'WEMIXUSDT'
    elif symbol == 'WBTCUSDT':
        return 'WBTCUSDT'
    elif symbol == 'CAKEUSDT':
        return 'CAKEUSDT'
    else:
        return symbol.replace('USDT.P', 'USDT')


def add_alert_history(alert: TradingViewAlert):
    with Session(engine) as session:
        ah = AlertHistory(
            source=alert.source,
            message_payload=alert.payload,
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


def add_limit_order_history(session, strategy_mgmt, exchange_symbol, order: BybitOrderResponse, formatted_amount,
                            alrt: TradingViewAlert):
    session.add(OrderHistory(
        order_id=order.id,
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
        exchange=strategy_mgmt.exchange,
        order_payload_1=order.payload
    ))
    session.commit()


def add_market_order_history(session, opn_mkt_odr: BybitOrderResponse, cls_mkt_odr: BybitFetchOrderResponse,
                             exchange_symbol, fund_diff, total_fund, filled_amt,
                             alrt: TradingViewAlert, strat_mgmt: StrategyManagement):
    session.add(OrderHistory(
        order_id=opn_mkt_odr.id,
        strategy_id=alrt.strategy_id,
        source_symbol=alrt.symbol,
        exchange_symbol=exchange_symbol,
        action=alrt.action,
        order_price=alrt.price,
        order_amt=filled_amt,
        active=False,
        exchange=strat_mgmt.exchange,
        order_status=cls_mkt_odr.order_status,
        avg_price=cls_mkt_odr.avg_price,
        exec_value=cls_mkt_odr.cum_exec_value,
        open_timestamp=cls_mkt_odr.created_time,
        open_datetime=cls_mkt_odr.get_open_datetime(),
        fill_timestamp=cls_mkt_odr.updated_time,
        fill_datetime=cls_mkt_odr.get_fill_datetime(),
        filled_amt=cls_mkt_odr.filled,
        fee_rate=cls_mkt_odr.get_fee_rate(),
        total_fee=cls_mkt_odr.cum_exec_fee,
        fund_diff=fund_diff,
        total_fund=total_fund,
        order_payload_1=opn_mkt_odr.payload,
        order_payload_2=cls_mkt_odr.payload,
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

    BITGET_PASSWORD = config['BitgetSettings']['password']
    BITGET_API_KEY = config['BitgetSettings']['key']
    BITGET_API_SECRET = config['BitgetSettings']['secret']
    bitget_exchange = ccxt.bitget({
        'password': BITGET_PASSWORD,
        'apiKey': BITGET_API_KEY,
        'secret': BITGET_API_SECRET
    })

    if config['BybitSettings']['set_sandbox_mode'] == 'True':
        bybit_exchange.set_sandbox_mode(True)
        bybit_exchange_per.set_sandbox_mode(True)

    def __init__(self):
        super().__init__()
        self.bybit_exchange.check_required_credentials()  # raises AuthenticationError
        self.bybit_exchange_per.check_required_credentials()  # raises AuthenticationError
        self.bitget_exchange.check_required_credentials()  # raises AuthenticationError
        markets = self.bybit_exchange.load_markets()
        markets1 = self.bybit_exchange_per.load_markets()
        markets2 = self.bitget_exchange.load_markets()

    def get_exchange_instance(self, strat: Strategy, strat_mgmt: StrategyManagement):
        if strat_mgmt.exchange == CryptoExchange.BYBIT.value:
            if strat.personal_acc:
                return self.bybit_exchange_per
            else:
                return self.bybit_exchange
        elif strat_mgmt.exchange == CryptoExchange.BITGET.value:
            return self.bitget_exchange

    def send_limit_order(self, strategy, strategy_mgmt, exchange_symbol, alrt: TradingViewAlert, exchange, session):
        if strategy_mgmt.exchange == CryptoExchange.BYBIT.value:
            amount = (strategy_mgmt.fund * strategy.position_size) / alrt.price
            if exchange_symbol == 'BTCUSDT' and amount < 0.001:
                formatted_amount = 0.001
            elif exchange_symbol == 'ETHUSDT' and amount < 0.01:
                formatted_amount = 0.01
            else:
                formatted_amount = exchange.amount_to_precision(exchange_symbol, amount)
            order_payload = exchange.create_limit_order(exchange_symbol, alrt.action, formatted_amount,
                                                        alrt.price)
            order_rsp = BybitOrderResponse(order_payload)

            add_limit_order_history(session, strategy_mgmt, exchange_symbol, order_rsp, formatted_amount,
                                    alrt)

    def place_order(self, tv_alrt):
        with Session(engine) as session:
            [(strategy,)] = session.execute(
                select(Strategy).where(Strategy.strategy_id == tv_alrt.strategy_id)).all()
            if not strategy.active:
                return
            strategy_mgmt_list = session.execute(
                select(StrategyManagement).where(StrategyManagement.strategy_id == tv_alrt.strategy_id)).all()
            for (strategy_mgmt,) in strategy_mgmt_list:
                strategy_mgmt: StrategyManagement
                if not strategy_mgmt.active:
                    continue
                exchange = self.get_exchange_instance(strategy, strategy_mgmt)
                exchange_symbol = symbol_translate(tv_alrt.symbol)
                if (strategy.direction == 'long' and tv_alrt.action == 'buy') or (
                        strategy.direction == 'short' and tv_alrt.action == 'sell'):
                    if strategy_mgmt.active_order:
                        raise Exception("There are still active order when opening position")
                    self.send_limit_order(strategy, strategy_mgmt, exchange_symbol, tv_alrt, exchange, session)
                    strategy_mgmt.active_order = True
                    session.commit()
                elif (strategy.direction == 'long' and tv_alrt.action == 'sell') or (
                        strategy.direction == 'short' and tv_alrt.action == 'buy'):
                    if not strategy_mgmt.active_order:
                        raise Exception("There is no active order when closing position")
                    existing_order_hist: OrderHistory = session.execute(select(OrderHistory)
                        .where(OrderHistory.strategy_id == tv_alrt.strategy_id)
                        .where(OrderHistory.exchange == strategy_mgmt.exchange)
                        .order_by(OrderHistory.created_at.desc()).limit(
                        1)).scalar_one()
                    if existing_order_hist.active:
                        existing_pos_order = BybitFetchOrderResponse(
                            exchange.fetch_order(existing_order_hist.order_id, exchange_symbol))
                        existing_order_hist.order_status = existing_pos_order.order_status
                        existing_order_hist.open_timestamp = existing_pos_order.created_time
                        existing_order_hist.open_datetime = existing_pos_order.get_open_datetime()
                        existing_order_hist.order_payload_2 = existing_pos_order.payload

                        if existing_pos_order.order_status != ExchangeOrderStatus.BYBIT_NEW.value:
                            existing_order_hist.avg_price = existing_pos_order.avg_price
                            existing_order_hist.exec_value = existing_pos_order.cum_exec_value
                            existing_order_hist.fill_timestamp = existing_pos_order.updated_time
                            existing_order_hist.fill_datetime = existing_pos_order.get_fill_datetime()
                            existing_order_hist.filled_amt = existing_pos_order.filled
                            existing_order_hist.fee_rate = existing_pos_order.get_fee_rate()
                            existing_order_hist.total_fee = existing_pos_order.cum_exec_fee
                            existing_order_hist.fund_diff = -existing_pos_order.cum_exec_fee
                            existing_order_hist.total_fund = existing_order_hist.total_fund - existing_pos_order.cum_exec_fee
                        session.flush()

                        if existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_NEW.value or existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_PARTIALLY_FILLED.value:
                            open_cnl_order = BybitOrderResponse(
                                exchange.cancel_order(existing_order_hist.order_id, exchange_symbol))
                            cls_cnl_order = BybitFetchOrderResponse(
                                exchange.fetch_order(open_cnl_order.id, exchange_symbol))
                            existing_order_hist.order_payload_2 = cls_cnl_order.payload  # overriding above
                            existing_order_hist.order_status = cls_cnl_order.order_status
                            existing_order_hist.active = False

                        if existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_PARTIALLY_FILLED.value:
                            open_mkt_order = BybitOrderResponse(
                                exchange.create_market_order(exchange_symbol, tv_alrt.action,
                                                             existing_order_hist.filled_amt))
                            closed_mkt_order = BybitFetchOrderResponse(exchange.fetch_order(open_mkt_order.id,
                                                                                            exchange_symbol))
                            if strategy.direction == 'long':
                                fund_diff = closed_mkt_order.cum_exec_value - existing_order_hist.exec_value - closed_mkt_order.cum_exec_fee
                            else:
                                fund_diff = existing_order_hist.exec_value - closed_mkt_order.cum_exec_value - closed_mkt_order.cum_exec_fee

                            total_fund = existing_order_hist.total_fund + fund_diff
                            add_market_order_history(session, open_mkt_order, closed_mkt_order, exchange_symbol,
                                                     fund_diff,
                                                     total_fund, existing_order_hist.filled_amt,
                                                     tv_alrt, strategy_mgmt)
                            strategy_mgmt.fund = total_fund

                        strategy_mgmt.active_order = False
                        session.commit()

    def process_msg(self, data):
        tv_alrt = TradingViewAlert(data)
        if is_duplicate_alert(tv_alrt):
            _ = add_alert_history(tv_alrt)
            return
        alert_id = add_alert_history(tv_alrt)
        try:
            self.place_order(tv_alrt)
        except Exception as e:
            print(traceback.format_exc())
            with Session(engine) as session:
                session.add(OrderExecutionError(
                    alert_id=alert_id,
                    error=str(e),
                    error_stack=traceback.format_exc()
                ))
                session.commit()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.process_msg(data)

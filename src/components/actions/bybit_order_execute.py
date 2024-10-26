import configparser
import os
import sys
# import time
import traceback
from typing import Any

import ccxt as ccxt
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from components.actions.base.action import Action

sys.path.append(os.path.split(os.getcwd())[0])

load_dotenv()
engine = create_engine(os.getenv('POSTGRESQL_URL'), echo=True)

from model.model import *


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


def add_order_history(session, strategy_mgmt, exchange_symbol, action, order, formatted_amount,
                      alrt: TradingViewAlert, executed_price):
    session.add(OrderHistory(
        order_id=order.id,
        strategy_id=alrt.strategy_id,
        source_symbol=alrt.symbol,
        exchange_symbol=exchange_symbol,
        action=action,
        order_price=alrt.price,
        order_amt=formatted_amount,
        active=True,
        position_size=executed_price * float(formatted_amount) / strategy_mgmt.fund,
        position_fund=executed_price * float(formatted_amount),
        total_fund=strategy_mgmt.fund,
        exchange=strategy_mgmt.exchange,
        order_payload_1=order.payload
    ))


def add_market_order_history(session, opn_mkt_odr, cls_mkt_odr,
                             exchange_symbol, action, fund_diff, total_fund, filled_amt,
                             alrt: TradingViewAlert, strat_mgmt: StrategyManagement):
    session.add(OrderHistory(
        order_id=opn_mkt_odr.id,
        strategy_id=alrt.strategy_id,
        source_symbol=alrt.symbol,
        exchange_symbol=exchange_symbol,
        action=action,
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
        total_fee=cls_mkt_odr.get_total_fee(),
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


def bybit_update_initial_order_history(eoh, epo):
    eoh.order_status = epo.order_status
    eoh.open_timestamp = epo.created_time
    eoh.open_datetime = epo.get_open_datetime()
    eoh.order_payload_2 = epo.payload


# def bitget_update_initial_order_history(eoh, epo):
#     eoh.order_status = epo.order_status
#     eoh.open_timestamp = epo.created_time
#     eoh.open_datetime = epo.get_open_datetime()
#     eoh.order_payload_2 = epo.payload
#
#
# def okex_update_initial_order_history(eoh, epo):
#     eoh.order_status = epo.order_status
#     eoh.open_timestamp = epo.created_time
#     eoh.open_datetime = epo.get_open_datetime()
#     eoh.order_payload_2 = epo.payload


def bybit_update_filled_order_history(eoh, epo, total_fund):
    eoh.avg_price = epo.avg_price
    eoh.exec_value = epo.cum_exec_value
    eoh.fill_timestamp = epo.updated_time
    eoh.fill_datetime = epo.get_fill_datetime()
    eoh.filled_amt = epo.filled
    eoh.fee_rate = epo.get_fee_rate()
    eoh.total_fee = epo.get_total_fee()
    eoh.fund_diff = -epo.get_total_fee()
    eoh.total_fund = total_fund


# def bitget_update_filled_order_history(eoh, epo):
#     eoh.avg_price = epo.avg_price
#     eoh.exec_value = epo.cum_exec_value
#     eoh.fill_timestamp = epo.updated_time
#     eoh.fill_datetime = epo.get_fill_datetime()
#     eoh.filled_amt = epo.filled
#     eoh.fee_rate = epo.get_fee_rate()
#     eoh.total_fee = epo.get_total_fee()
#     eoh.fund_diff = -epo.get_total_fee()
#     eoh.total_fund = eoh.total_fund - epo.get_total_fee()
#
#
# def okex_update_filled_order_history(eoh, epo: OkexFetchOrderResponse):
#     eoh.avg_price = epo.avg_price
#     eoh.exec_value = epo.cum_exec_value
#     eoh.fill_timestamp = epo.updated_time
#     eoh.fill_datetime = epo.get_fill_datetime()
#     eoh.filled_amt = epo.filled
#     eoh.fee_rate = epo.get_fee_rate()
#     eoh.total_fee = epo.get_total_fee()
#     eoh.fund_diff = -epo.get_total_fee()
#     eoh.total_fund = eoh.total_fund - epo.get_total_fee()


def bybit_cancel_unfilled_new_order(eoh, exchange, exchange_symbol):
    open_cnl_order = BybitOrderResponse(
        exchange.cancel_order(eoh.order_id, exchange_symbol))
    cls_cnl_order = BybitFetchOrderResponse(bybit_fetch_order(exchange, open_cnl_order.id, exchange_symbol))
    eoh.order_payload_2 = cls_cnl_order.payload  # overriding above
    eoh.order_status = cls_cnl_order.order_status
    eoh.active = False


# def bitget_cancel_unfilled_new_order(eoh, exchange, exchange_symbol):
#     open_cnl_order = BitgetOrderResponse(
#         exchange.cancel_order(eoh.order_id, exchange_symbol))
#     order_resp = exchange.fetch_order(open_cnl_order.id, exchange_symbol)
#     print(order_resp)
#     cls_cnl_order = BitgetFetchOrderResponse(order_resp)
#     eoh.order_payload_2 = cls_cnl_order.payload  # overriding above
#     eoh.order_status = cls_cnl_order.order_status
#     eoh.active = False
#
#
# def okex_cancel_unfilled_new_order(eoh, exchange, exchange_symbol):
#     open_cnl_order = OkexOrderResponse(
#         exchange.cancel_order(eoh.order_id, exchange_symbol))
#     cls_cnl_order = OkexFetchOrderResponse(
#         exchange.fetch_order(open_cnl_order.id, exchange_symbol))
#     eoh.order_payload_2 = cls_cnl_order.payload  # overriding above
#     eoh.order_status = cls_cnl_order.order_status
#     eoh.active = False


def bybit_close_market_order(exchange, exchange_symbol, action, amt):
    open_mkt_order = BybitOrderResponse(
        exchange.create_market_order(exchange_symbol, action, amt))
    order_resp = bybit_fetch_order(exchange, open_mkt_order.id, exchange_symbol)
    print(order_resp)
    return open_mkt_order, BybitFetchOrderResponse(order_resp)


# def bitget_close_market_order(exchange, exchange_symbol, action, amt):
#     open_mkt_order = BitgetOrderResponse(
#         exchange.create_market_order(exchange_symbol, action, amt, params={'oneWayMode': True}))
#     order_resp = exchange.fetch_order(open_mkt_order.id, exchange_symbol)
#     try_count = 0
#     while order_resp['status'] == 'open' and try_count < 4:
#         print("Order Still Open, retrying...")
#         time.sleep(1)
#         order_resp = exchange.fetch_order(open_mkt_order.id, exchange_symbol)
#         try_count += 1
#     print(order_resp)
#     return open_mkt_order, BitgetFetchOrderResponse(order_resp)
#
#
# def okex_close_market_order(exchange, exchange_symbol, action, amt, params):
#     open_mkt_order = OkexOrderResponse(
#         exchange.create_market_order(exchange_symbol, action, amt, params))
#     order_resp = exchange.fetch_order(open_mkt_order.id, exchange_symbol)
#     print(order_resp)
#     return open_mkt_order, OkexFetchOrderResponse(order_resp)


def bybit_fetch_order(exchange, order_id, exchange_symbol):
    try:
        return exchange.fetch_closed_order(order_id, exchange_symbol)
    except ccxt.OrderNotFound:
        return exchange.fetch_open_order(order_id, exchange_symbol)


class BybitOrderExecute(Action):
    bybit_exchange: Any
    bybit_exchange_per: Any

    # bitget_exchange: Any
    # bitget_exchange_sandbox_mode = False
    # okex_exchange_sandbox_mode = False

    def __init__(self):
        super().__init__()

        config = configparser.ConfigParser()
        config.read('config.ini')
        API_KEY = config['BybitSettings']['key']
        API_SECRET = config['BybitSettings']['secret']
        self.bybit_exchange = ccxt.bybit({
            'apiKey': API_KEY,
            'secret': API_SECRET
        })

        API_KEY_PERSONAL = config['BybitSettings']['key_personal']
        API_SECRET_PERSONAL = config['BybitSettings']['secret_personal']
        self.bybit_exchange_per = ccxt.bybit({
            'apiKey': API_KEY_PERSONAL,
            'secret': API_SECRET_PERSONAL
        })

        # BITGET_PASSWORD = config['BitgetSettings']['password']
        # BITGET_API_KEY = config['BitgetSettings']['key']
        # BITGET_API_SECRET = config['BitgetSettings']['secret']
        # self.bitget_exchange = ccxt.bitget({
        #     'password': BITGET_PASSWORD,
        #     'apiKey': BITGET_API_KEY,
        #     'secret': BITGET_API_SECRET
        # })
        #
        # OKEX_PASSWORD = config['OkexSettings']['password']
        # OKEX_API_KEY = config['OkexSettings']['key']
        # OKEX_API_SECRET = config['OkexSettings']['secret']
        # self.okex_exchange = ccxt.okx({
        #     'password': OKEX_PASSWORD,
        #     'apiKey': OKEX_API_KEY,
        #     'secret': OKEX_API_SECRET
        # })

        if config['BybitSettings']['set_sandbox_mode'] == 'True':
            self.bybit_exchange.set_sandbox_mode(True)
            self.bybit_exchange_per.set_sandbox_mode(True)

        # if config['OkexSettings']['set_sandbox_mode'] == 'True':
        #     self.okex_exchange.set_sandbox_mode(True)
        #     self.okex_exchange_sandbox_mode = True
        #
        # if config['BitgetSettings']['set_sandbox_mode'] == 'True':
        #     self.bitget_exchange.set_sandbox_mode(True)
        #     self.bitget_exchange_sandbox_mode = True

        self.bybit_exchange.check_required_credentials()  # raises AuthenticationError
        self.bybit_exchange_per.check_required_credentials()  # raises AuthenticationError
        # self.bitget_exchange.check_required_credentials()  # raises AuthenticationError
        # self.okex_exchange.check_required_credentials()  # raises AuthenticationError
        markets = self.bybit_exchange.load_markets()
        markets1 = self.bybit_exchange_per.load_markets()
        # markets2 = self.bitget_exchange.load_markets()
        # markets3 = self.okex_exchange.load_markets()
        # f = open("demofile3.txt", "a")
        # f.write(str(markets3))
        # f.close()

    def get_exchange_instance(self, strat: Strategy, strat_mgmt: StrategyManagement):
        if strat_mgmt.exchange == CryptoExchange.BYBIT.value:
            if strat.personal_acc:
                return self.bybit_exchange_per
            else:
                return self.bybit_exchange
        # elif strat_mgmt.exchange == CryptoExchange.BITGET.value:
        #     return self.bitget_exchange
        # elif strat_mgmt.exchange == CryptoExchange.OKEX.value:
        #     return self.okex_exchange

    def symbol_translate(self, symbol, exchange):
        if exchange == CryptoExchange.BYBIT.value:
            return symbol.replace('USDT.P', 'USDT')
        # elif exchange == CryptoExchange.BITGET.value and self.bitget_exchange_sandbox_mode:
        #     if 'USDT.P' in symbol:
        #         symbol = symbol.replace('USDT.P', '/SUSDT')
        #     else:
        #         symbol = symbol.replace('USDT', '/SUSDT')
        #     return f'S{symbol}:SUSDT'
        # elif exchange == CryptoExchange.BITGET.value and not self.bitget_exchange_sandbox_mode:
        #     if symbol == 'SHIB1000USDT.P':
        #         return 'SHIB/USDT:USDT'
        #     elif symbol == '1000PEPEUSDT.P':
        #         return 'PEPE/USDT:USDT'
        #     elif symbol == '1000FLOKIUSDT.P':
        #         return 'FLOKI/USDT:USDT'
        #     elif symbol == '1000LUNCUSDT.P':
        #         return 'LUNC/USDT:USDT'
        #     elif symbol == 'HNTUSDT.P':
        #         return 'HNT/USDT'
        #     elif symbol == 'CROUSDT.P':
        #         return 'CRO/USDT'
        #     elif symbol == 'WBTCUSDT':
        #         return 'WBTC/USDT'
        #     elif symbol == 'WEMIXUSDT.P':
        #         return 'WEMIX/USDT'
        #     elif symbol == 'RAYUSDT':
        #         return 'RAY/USDT'
        #     elif symbol == 'OSMOUSDT':
        #         return 'OSMO/USDT'
        #     elif symbol == 'RIFUSDT.P':
        #         return 'RIF/USDT'
        #     elif symbol == 'YFIUSDT.P':
        #         return 'YFI/USDT'
        #     elif symbol == 'STETHUSDT':
        #         return 'STETH/USDT'
        #     elif symbol == 'GNOUSDT':
        #         return 'GNO/USDT'
        #     if 'USDT.P' in symbol:
        #         symbol = symbol.replace('USDT.P', '/USDT')
        #     else:
        #         symbol = symbol.replace('USDT', '/USDT')
        #     return f'{symbol}:USDT'
        # elif exchange == CryptoExchange.OKEX.value:
        #     if symbol == 'SHIB1000USDT.P':
        #         return 'SHIB/USDT'
        #     elif symbol == '1000PEPEUSDT.P':
        #         return 'PEPE/USDT'
        #     elif symbol == '1000XECUSDT.P':
        #         return 'XEC/USDT'
        #     elif symbol == '1000FLOKIUSDT.P':
        #         return 'FLOKI/USDT'
        #     elif symbol == '1000LUNCUSDT.P':
        #         return 'LUNC/USDT'
        #     elif symbol == 'STETHUSDT':
        #         return 'STETH/USDT'
        #     if 'USDT.P' in symbol:
        #         return symbol.replace('USDT.P', '/USDT')
        #     else:
        #         return symbol.replace('USDT', '/USDT')

    def format_amount(self, strategy_mgmt: StrategyManagement, exchange_symbol, amount, exchange):
        if strategy_mgmt.exchange == CryptoExchange.BYBIT.value:
            if exchange_symbol == 'BTCUSDT' and amount < 0.001:
                formatted_amount = 0.001
            elif exchange_symbol == 'ETHUSDT' and amount < 0.01:
                formatted_amount = 0.01
            elif exchange_symbol == 'SUIUSDT' and amount < 10:
                formatted_amount = 10
            else:
                formatted_amount = exchange.amount_to_precision(exchange_symbol, amount)
            return formatted_amount

    def send_limit_order(self, strategy: Strategy, strategy_mgmt: StrategyManagement, exchange_symbol,
                         alrt: TradingViewAlert, exchange,
                         session):
        if strategy.leverage is None or strategy.leverage == 0 or not strategy.is_lev or strategy.is_lev is None:
            amount = (strategy_mgmt.fund * strategy.position_size) / alrt.price
        else:
            amount = ((strategy_mgmt.fund * strategy.position_size) / alrt.price) * strategy.leverage
        formatted_amount = self.format_amount(strategy_mgmt, exchange_symbol, amount, exchange)
        order_payload = exchange.create_limit_order(exchange_symbol, alrt.action, formatted_amount,
                                                    alrt.price)
        order_rsp = BybitOrderResponse(order_payload)
        add_order_history(session, strategy_mgmt, exchange_symbol, alrt.action, order_rsp, formatted_amount,
                          alrt, alrt.price)

    def send_pair_market_order(self, strategy: Strategy, strategy_mgmt, exchange_symbol, alrt: TradingViewAlert,
                               exchange,
                               session):
        pair_symbol_list = exchange_symbol.split("/")
        if alrt.action == 'buy':
            [long_sym, short_sym] = pair_symbol_list
        elif alrt.action == 'sell':
            [short_sym, long_sym] = pair_symbol_list
        long_sym_last_price = exchange.fetch_ticker(long_sym)['last']
        short_sym_last_price = exchange.fetch_ticker(short_sym)['last']

        for symbol, price, side in [(long_sym, long_sym_last_price, 'buy'), (short_sym, short_sym_last_price, 'sell')]:
            if strategy.leverage is None or strategy.leverage == 0 or not strategy.is_lev or strategy.is_lev is None:
                amount = ((strategy_mgmt.fund / 2) * strategy.position_size) / price
            else:
                amount = (((strategy_mgmt.fund / 2) * strategy.position_size) / price) * strategy.leverage
            formatted_amount = self.format_amount(strategy_mgmt, symbol, amount, exchange)
            order_payload = exchange.create_market_order(symbol, side, formatted_amount)
            order_rsp = BybitOrderResponse(order_payload)
            add_order_history(session, strategy_mgmt, symbol, side, order_rsp, formatted_amount,
                              alrt, price)

        # elif strategy_mgmt.exchange == CryptoExchange.BITGET.value:
        #     bitget_odr_price = alrt.price
        #     if exchange_symbol == 'SBTC/SUSDT:SUSDT' and amount < 0.002:
        #         formatted_amount = 0.002
        #     elif exchange_symbol == 'SETH/SUSDT:SUSDT' and amount < 0.01:
        #         formatted_amount = 0.01
        #     elif exchange_symbol == 'BTC/USDT:USDT' and amount < 0.002:
        #         formatted_amount = 0.002
        #     elif exchange_symbol == 'WBTC/USDT' and amount < 0.002:
        #         formatted_amount = 0.002
        #     elif exchange_symbol == 'ETH/USDT:USDT' and amount < 0.01:
        #         formatted_amount = 0.01
        #     elif exchange_symbol == 'STETH/USDT:USDT' and amount < 0.01:
        #         formatted_amount = 0.01
        #     elif exchange_symbol == 'SOL/USDT:USDT' and amount < 1:
        #         formatted_amount = 0.1
        #     elif exchange_symbol == 'HNT/USDT' and amount < 1:
        #         formatted_amount = 1
        #     elif exchange_symbol == 'SHIB/USDT:USDT' or \
        #             exchange_symbol == 'PEPE/USDT:USDT' or \
        #             exchange_symbol == 'FLOKI/USDT:USDT' or \
        #             exchange_symbol == 'LUNC/USDT:USDT':
        #         bitget_odr_price = alrt.price / 1000
        #         formatted_amount = exchange.amount_to_precision(exchange_symbol, amount * 1000)
        #     else:
        #         formatted_amount = exchange.amount_to_precision(exchange_symbol, amount)
        #     action = alrt.action
        #     try:
        #         order_payload = exchange.create_limit_order(exchange_symbol, action, formatted_amount, bitget_odr_price,
        #                                                     params={'oneWayMode': True})
        #     except ccxt.ExchangeError as e:
        #         if f'''"code":"{BitgetErrorCode.ORDER_PRICE_HIGHER_THAN_BID_PRICE.value}"''' in str(
        #                 e) or f'''"code":"{BitgetErrorCode.ORDER_PRICE_LOWER_THAN_BID_PRICE.value}"''' in str(e):
        #             order_payload = exchange.create_market_order(exchange_symbol, action, formatted_amount,
        #                                                          bitget_odr_price, params={'oneWayMode': True})
        #         else:
        #             raise e
        #     order_rsp = BitgetOrderResponse(order_payload)
        #     add_limit_order_history(session, strategy_mgmt, exchange_symbol, order_rsp, formatted_amount,
        #                             alrt, bitget_odr_price)
        #
        # elif strategy_mgmt.exchange == CryptoExchange.OKEX.value:
        #     params = {}
        #     # if not self.okex_exchange_sandbox_mode:
        #     #     params = {'tdMode': 'spot_isolated'}
        #     okex_odr_price = alrt.price
        #     if exchange_symbol == 'SHIB/USDT' or \
        #             exchange_symbol == 'PEPE/USDT' or \
        #             exchange_symbol == 'XEC/USDT' or \
        #             exchange_symbol == 'FLOKI/USDT' or \
        #             exchange_symbol == 'LUNC/USDT':
        #         okex_odr_price = alrt.price / 1000
        #         if exchange_symbol == 'FLOKI/USDT' and (1000 * amount) < 100000:
        #             formatted_amount = 110000
        #         else:
        #             formatted_amount = exchange.amount_to_precision(exchange_symbol, 1000 * amount)
        #     elif exchange_symbol == 'FET/USDT' and amount < 10:
        #         formatted_amount = 11
        #     else:
        #         formatted_amount = exchange.amount_to_precision(exchange_symbol, amount)
        #     try:
        #         order_payload = exchange.create_limit_order(exchange_symbol, alrt.action, formatted_amount,
        #                                                     okex_odr_price,
        #                                                     params=params)
        #     except ccxt.ExchangeError as e:
        #         if f'''"sCode":"{OkexErrorCode.THE_HIGHEST_PRICE_LIMIT_FOR_BUY_ORDERS.value}"''' in str(
        #                 e) or f'''"sCode":"{OkexErrorCode.THE_LOWEST_PRICE_LIMIT_FOR_SELL_ORDERS.value}"''' in str(e):
        #             order_payload = exchange.create_market_order(exchange_symbol, alrt.action, formatted_amount,
        #                                                          params=params)
        #         else:
        #             raise e
        #     order_rsp = OkexOrderResponse(order_payload)
        #     add_limit_order_history(session, strategy_mgmt, exchange_symbol, order_rsp, formatted_amount,
        #                             alrt, okex_odr_price)

    def place_order_in_exchange(self, tv_alrt, strategy, strategy_mgmt, session):
        exchange = self.get_exchange_instance(strategy, strategy_mgmt)
        exchange_symbol = self.symbol_translate(tv_alrt.symbol, strategy_mgmt.exchange)
        if (strategy.direction == StrategyDirection.LONG.value and tv_alrt.action == 'buy') or \
                (strategy.direction == StrategyDirection.SHORT.value and tv_alrt.action == 'sell'):
            if strategy_mgmt.active_order:
                raise Exception("There are still active order when opening position")
            self.send_limit_order(strategy, strategy_mgmt, exchange_symbol, tv_alrt, exchange, session)
            strategy_mgmt.active_order = True
            session.commit()
        elif (strategy.direction == StrategyDirection.PAIR_LONG.value and tv_alrt.action == 'buy') or \
                (strategy.direction == StrategyDirection.PAIR_SHORT.value and tv_alrt.action == 'sell'):
            if strategy_mgmt.active_order:
                raise Exception("There are still active order when opening position")
            self.send_pair_market_order(strategy, strategy_mgmt, exchange_symbol, tv_alrt, exchange, session)
            strategy_mgmt.active_order = True
            session.commit()
        elif (strategy.direction == StrategyDirection.LONG.value and tv_alrt.action == 'sell') or \
                (strategy.direction == StrategyDirection.SHORT.value and tv_alrt.action == 'buy') or \
                (strategy.direction == StrategyDirection.PAIR_LONG.value and tv_alrt.action == 'sell') or \
                (strategy.direction == StrategyDirection.PAIR_SHORT.value and tv_alrt.action == 'buy'):
            if not strategy_mgmt.active_order:
                raise Exception("There is no active order when closing position")
            existing_order_hist_list = session.execute(select(OrderHistory)
                                                       .where(OrderHistory.strategy_id == tv_alrt.strategy_id)
                                                       .where(OrderHistory.exchange == strategy_mgmt.exchange)
                                                       .where(OrderHistory.active)).all()

            for (existing_order_hist,) in existing_order_hist_list:
                existing_order_hist: OrderHistory
                existing_pos_order = None
                if strategy_mgmt.exchange == CryptoExchange.BYBIT.value:
                    order_resp = bybit_fetch_order(exchange, existing_order_hist.order_id,
                                                   existing_order_hist.exchange_symbol)
                    print(order_resp)
                    existing_pos_order = BybitFetchOrderResponse(order_resp)
                    bybit_update_initial_order_history(existing_order_hist, existing_pos_order)
                # elif strategy_mgmt.exchange == CryptoExchange.BITGET.value:
                #     print(exchange.fetch_order(existing_order_hist.order_id, exchange_symbol))
                #     existing_pos_order = BitgetFetchOrderResponse(
                #         exchange.fetch_order(existing_order_hist.order_id, exchange_symbol))
                #     bitget_update_initial_order_history(existing_order_hist, existing_pos_order)
                # elif strategy_mgmt.exchange == CryptoExchange.OKEX.value:
                #     print(exchange.fetch_order(existing_order_hist.order_id, exchange_symbol))
                #     existing_pos_order = OkexFetchOrderResponse(
                #         exchange.fetch_order(existing_order_hist.order_id, exchange_symbol))
                #     okex_update_initial_order_history(existing_order_hist, existing_pos_order)

                if strategy_mgmt.exchange == CryptoExchange.BYBIT.value and existing_pos_order.order_status != ExchangeOrderStatus.BYBIT_NEW.value:
                    strategy_mgmt.fund = strategy_mgmt.fund - existing_pos_order.get_total_fee()
                    bybit_update_filled_order_history(existing_order_hist, existing_pos_order, strategy_mgmt.fund)
                # elif strategy_mgmt.exchange == CryptoExchange.BITGET.value and existing_pos_order.order_status != ExchangeOrderStatus.BITGET_NEW.value:
                #     bitget_update_filled_order_history(existing_order_hist, existing_pos_order)
                # elif strategy_mgmt.exchange == CryptoExchange.OKEX.value and existing_pos_order.order_status != ExchangeOrderStatus.OKEX_NEW.value:
                #     okex_update_filled_order_history(existing_order_hist, existing_pos_order)
                session.flush()

                if strategy_mgmt.exchange == CryptoExchange.BYBIT.value and (
                        existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_NEW.value or existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_PARTIALLY_FILLED.value):
                    bybit_cancel_unfilled_new_order(existing_order_hist, exchange, existing_order_hist.exchange_symbol)
                # elif strategy_mgmt.exchange == CryptoExchange.BITGET.value and (
                #         existing_pos_order.order_status == ExchangeOrderStatus.BITGET_NEW.value or existing_pos_order.order_status == ExchangeOrderStatus.BITGET_PARTIALLY_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.BITGET_SPOT_FILLED.value):
                #     bitget_cancel_unfilled_new_order(existing_order_hist, exchange, exchange_symbol)
                # elif strategy_mgmt.exchange == CryptoExchange.OKEX.value and (
                #         existing_pos_order.order_status == ExchangeOrderStatus.OKEX_NEW.value or existing_pos_order.order_status == ExchangeOrderStatus.OKEX_PARTIALLY_FILLED.value):
                #     okex_cancel_unfilled_new_order(existing_order_hist, exchange, exchange_symbol)

                if strategy_mgmt.exchange == CryptoExchange.BYBIT.value and (
                        existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.BYBIT_PARTIALLY_FILLED.value):
                    order_action = 'sell' if existing_order_hist.action == 'buy' else 'buy'
                    open_mkt_order, closed_mkt_order = bybit_close_market_order(exchange,
                                                                                existing_order_hist.exchange_symbol,
                                                                                order_action,
                                                                                existing_order_hist.filled_amt)
                    fund_diff = strategy.calculate_fund_diff(closed_mkt_order.cum_exec_value,
                                                             existing_order_hist.exec_value,
                                                             closed_mkt_order.get_total_fee())
                    strategy_mgmt.fund = strategy_mgmt.fund + fund_diff
                    add_market_order_history(session, open_mkt_order, closed_mkt_order,
                                             existing_order_hist.exchange_symbol, order_action,
                                             fund_diff,
                                             strategy_mgmt.fund, existing_order_hist.filled_amt,
                                             tv_alrt, strategy_mgmt)
                # elif strategy_mgmt.exchange == CryptoExchange.BITGET.value and (
                #         existing_pos_order.order_status == ExchangeOrderStatus.BITGET_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.BITGET_PARTIALLY_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.BITGET_SPOT_FILLED.value):
                #     action = tv_alrt.action
                #     open_mkt_order, closed_mkt_order = bitget_close_market_order(exchange, exchange_symbol,
                #                                                                  action,
                #                                                                  existing_order_hist.filled_amt)
                #     fund_diff = strategy.calculate_fund_diff(closed_mkt_order.cum_exec_value,
                #                                              existing_order_hist.exec_value,
                #                                              closed_mkt_order.get_total_fee())
                #     strategy_mgmt.fund = existing_order_hist.total_fund + fund_diff
                #     add_market_order_history(session, open_mkt_order, closed_mkt_order, exchange_symbol,
                #                              fund_diff,
                #                              strategy_mgmt.fund, existing_order_hist.filled_amt,
                #                              tv_alrt, strategy_mgmt)
                # elif strategy_mgmt.exchange == CryptoExchange.OKEX.value and (
                #         existing_pos_order.order_status == ExchangeOrderStatus.OKEX_FILLED.value or existing_pos_order.order_status == ExchangeOrderStatus.OKEX_PARTIALLY_FILLED.value):
                #     params = {}
                #     # if not self.okex_exchange_sandbox_mode:
                #     #     params = {'tdMode': 'spot_isolated'}
                #     open_mkt_order, closed_mkt_order = okex_close_market_order(exchange, exchange_symbol,
                #                                                                tv_alrt.action,
                #                                                                existing_order_hist.filled_amt, params)
                #     fund_diff = strategy.calculate_fund_diff(closed_mkt_order.cum_exec_value,
                #                                              existing_order_hist.exec_value,
                #                                              closed_mkt_order.get_total_fee())
                #     strategy_mgmt.fund = existing_order_hist.total_fund + fund_diff
                #     add_market_order_history(session, open_mkt_order, closed_mkt_order, exchange_symbol,
                #                              fund_diff,
                #                              strategy_mgmt.fund, existing_order_hist.filled_amt,
                #                              tv_alrt, strategy_mgmt)
                existing_order_hist.active = False
                strategy_mgmt.active_order = False
                session.commit()

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
                try:
                    self.place_order_in_exchange(tv_alrt, strategy, strategy_mgmt, session)
                except Exception as e:
                    print(traceback.format_exc())
                    session.add(OrderExecutionError(
                        alert_id=tv_alrt.id,
                        error=str(e),
                        error_stack=traceback.format_exc(),
                        exchange=strategy_mgmt.exchange
                    ))
                    session.commit()

    def process_msg(self, data):
        tv_alrt = TradingViewAlert(data)
        if is_duplicate_alert(tv_alrt):
            _ = add_alert_history(tv_alrt)
            return
        tv_alrt.id = add_alert_history(tv_alrt)
        try:
            self.place_order(tv_alrt)
        except Exception as e:
            print(traceback.format_exc())
            with Session(engine) as session:
                session.add(OrderExecutionError(
                    alert_id=tv_alrt.id,
                    error=str(e),
                    error_stack=traceback.format_exc()
                ))
                session.commit()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.process_msg(data)

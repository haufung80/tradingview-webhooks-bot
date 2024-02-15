from datetime import datetime

from pytest_bdd import scenarios, given, then, parsers
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from components.actions.bybit_order_execute import BybitOrderExecute
from model.model import OrderExecutionError

engine = create_engine('postgresql://postgres:1234@localhost/tradingview-webhooks-bot', echo=True)
session = Session(engine)

scenarios("bybit_order_execute.feature")


@given(parsers.parse(
    "Incoming tradingview alert of {strategy_id},{action},{price},{symbol},{exchange},{source}"),
    target_fixture="err_num")
def given_cucumbers(strategy_id, action, price, symbol, exchange, source):
    with Session(engine) as session:
        err_num = session.execute(select(func.count("*")).select_from(OrderExecutionError)).scalar_one()
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    tv_alert_dict = {
        "key": "BybitWebhook:xxxxxx",
        "data": {
            "strategy_id": strategy_id,
            "action": action,
            "position_size": "2992.085",
            "price": price,
            "symbol": symbol,
            "timestamp": timestamp,
            "exchange": exchange,
            "source": source,
            "noofcontracts": "2992.085",
            "orderid": "long",
            "comment": "long",
            "alert_msg": "",
            "market_position": "long",
            "market_position_size": "2992.085",
            "prev_market_position": "flat",
            "prev_market_position_size": "0"
        }
    }
    bybit_order_execute = BybitOrderExecute()
    bybit_order_execute.process_msg(tv_alert_dict)
    return err_num


@then(parsers.parse("There should be no error"))
def should_have_left_cucumbers(err_num):
    with Session(engine) as session:
        new_err_num = session.execute(select(func.count("*")).select_from(OrderExecutionError)).scalar_one()
    assert err_num == new_err_num

import configparser

from components.actions.base.action import Action
from futu import *


class FutuOrderExecute(Action):
    config = configparser.ConfigParser()
    config.read('config.ini')
    pwd_unlock = config['FutuSettings']['pwd_unlock']

    def __init__(self):
        super().__init__()

    def place_order(self, data):
        trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111,
                                      security_firm=SecurityFirm.FUTUSECURITIES)
        ret, data = trd_ctx.unlock_trade(self.pwd_unlock)  # If you use a live trading account to place an order, you need to unlock the account first. The example here is to place an order on a paper trading account, and unlocking is not necessary.
        if ret == RET_OK:
            ret, data = trd_ctx.place_order(price=0, qty=100, order_type=OrderType.MARKET, code="HK.07200", trd_side=TrdSide.BUY,
                                            trd_env=TrdEnv.SIMULATE)
            if ret == RET_OK:
                print(data)
                print(data['order_id'][0])  # Get the order ID of the placed order
                print(data['order_id'].values.tolist())  # Convert to list
            else:
                print('place_order error: ', data)
        else:
            print('unlock_trade failed: ', data)
        trd_ctx.close()

    def run(self, *args, **kwargs):
        data = self.validate_data()
        self.place_order(data['data'])

        super().run(*args, **kwargs)  # this is required

        print(self.name, '---> action has run!')

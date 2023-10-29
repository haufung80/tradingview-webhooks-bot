import asyncio

from components.actions.base.action import Action
from ib_insync import *

from retry import retry

util.logToConsole()
ib = IB()


# @retry(delay=10)
def connect_ib():
    ib.connect('127.0.0.1', 4001, clientId=0)


connect_ib()


class IBOrderExecute(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Add your custom logic here.
        """
        print(self.name, '---> action has run!')
        data = self.validate_data()['data']
        print('Data:', data)

        order_obj = data['order']
        order = MarketOrder(order_obj['action'], order_obj['totalQuantity'])

        contract_obj = data['contract']
        sec_type = contract_obj['secType']
        if sec_type == 'STK':
            contract = Stock(contract_obj['symbol'], contract_obj['exchange'], contract_obj['currency'])
        else:
            contract = None
        trade = ib.placeOrder(contract, order)
        while not trade.isDone():
            ib.waitOnUpdate()
        print('Trade Log:', trade.log)

        return 'OK'

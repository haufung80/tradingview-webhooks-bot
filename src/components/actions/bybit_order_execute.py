from components.actions.base.action import Action
import ccxt as ccxt
import configparser


class BybitOrderExecute(Action):
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['BybitSettings']['key']
    API_SECRET = config['BybitSettings']['secret']
    exchange = ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET
    })
    def __init__(self):
        super().__init__()
        self.exchange.check_required_credentials()  # raises AuthenticationError

    def place_order(self, data):
        markets = self.exchange.load_markets()
        formatted_amount = self.exchange.amount_to_precision(data['symbol'], data['amount'])
        order = self.exchange.create_market_order(data['symbol'], data['action'], formatted_amount)
        print(order)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.place_order(data['data'])

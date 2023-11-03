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
        markets = self.exchange.load_markets()

    def place_order(self, data):
        symbol = None

        if data['symbol'] == 'BTCUSDT.P':
            symbol = 'BTCUSDT'
        elif data['symbol'] == 'BNBUSDT.P':
            symbol = 'BNBUSDT'

        formatted_amount = self.exchange.amount_to_precision(symbol, float(data['amount']))
        order = self.exchange.create_market_order(symbol, data['action'], formatted_amount)
        print(order)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.place_order(data['data'])

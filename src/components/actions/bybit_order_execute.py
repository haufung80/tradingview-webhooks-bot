from components.actions.base.action import Action
import ccxt as ccxt
import configparser
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.split(os.getcwd())[0])

load_dotenv()
engine = create_engine(os.getenv('POSTGRESQL_URL'), echo=True)

from src.model.model import AlertHistory


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
        symbol = None
        if data['symbol'] == 'BTCUSDT.P':
            symbol = 'BTCUSDT'
        elif data['symbol'] == 'BNBUSDT.P':
            symbol = 'BNBUSDT'

        with Session(engine) as session:
            session.add(AlertHistory(
                source=data['source'],
                message_payload=data,
                strategy_id=data['strategy_id'],
                timestamp=datetime.fromtimestamp(data['timestamp']),
                symbol=data['symbol'],
                exchange=data['exchange'],
                action=data['action'],
                price=data['price'],
            ))
            session.commit()

        formatted_amount = self.exchange.amount_to_precision(symbol, float(data['amount']))
        order = self.exchange.create_limit_order(symbol, data['action'], formatted_amount, data['price'])
        print(order)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        print(self.name, '---> action has run!')
        data = self.validate_data()
        self.place_order(data['data'])

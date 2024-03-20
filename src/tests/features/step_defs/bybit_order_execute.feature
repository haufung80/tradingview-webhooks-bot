# content of scenario_outlines.feature

Feature: Placing Order to different exchanges

  Scenario Outline: Placing Order to Bybit Exchange
    Given Incoming tradingview alert of <strategy_id>,<action>,<price>,<symbol>,<exchange>,<source>
    Then There should be one order_history added
    Then There should be no error

    Examples:
      | strategy_id                       | action | price | symbol    | exchange | source      |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_BTC | buy    | 67000 | BTCUSDT.P | BYBIT    | tradingview |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_BTC | sell   | 67000 | BTCUSDT.P | BYBIT    | tradingview |
#      | SMA_CROSSOVER_WBTC | buy    | 69000 | WBTCUSDT | BYBIT    | tradingview |
#      | SMA_CROSSOVER_WBTC | sell   | 69000 | WBTCUSDT | BYBIT    | tradingview |
      | SMA_CROSSOVER_LONG_1D_BTC         | buy    | 67000 | BTCUSDT.P | BITGET   | tradingview |
      | SMA_CROSSOVER_LONG_1D_BTC         | sell   | 67000 | BTCUSDT.P | BITGET   | tradingview |
#      | MACD_CROSSOVER_WBTC | buy    | 69000 | WBTCUSDT | BITGET    | tradingview |
#      | MACD_CROSSOVER_WBTC | sell   | 69000 | WBTCUSDT | BITGET    | tradingview |
      | STOCH_OSCILL_MOMENTUM_LONG_4H_BTC | buy    | 67000 | BTCUSDT.P | OKEX     | tradingview |
      | STOCH_OSCILL_MOMENTUM_LONG_4H_BTC | sell   | 67000 | BTCUSDT.P | OKEX     | tradingview |


#Scenario Outline: Filter duplicated alert
# Given There is an incoming aleırt,
#  When there is already same alert in alert_history table
#  Then it should record the alert and do not execute anything
#
#Scenario Outline: Handle BTC 0.001 and ETH 0.01 minimal bet issue in bybit
# content of scenario_outlines.feature

Feature: Placing Order to different exchanges

  Scenario Outline: Placing Order to Bybit Exchange
    Given Incoming tradingview alert of <strategy_id>,<action>,<price>,<symbol>,<exchange>,<source>
    Then There should be no error

    Examples:
      | strategy_id                       | action | price | symbol    | exchange | source      |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_BTC | buy    | 60000 | BTCUSDT.P | BYBIT    | tradingview |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_BTC | sell   | 60000 | BTCUSDT.P | BYBIT    | tradingview |


#Scenario Outline: Filter duplicated alert
# Given There is an incoming aleırt,
#  When there is already same alert in alert_history table
#  Then it should record the alert and do not execute anything
#
#Scenario Outline: Handle BTC 0.001 and ETH 0.01 minimal bet issue in bybit
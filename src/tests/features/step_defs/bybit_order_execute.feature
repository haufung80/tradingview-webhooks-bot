# content of scenario_outlines.feature

Feature: Placing Order to different exchanges

  Scenario Outline: Placing Order to Bybit Exchange
    Given Incoming tradingview alert of <strategy_id>,<action>,<price>,<symbol>,<timestamp>,<exchange>,<source>
    Then There should be no error

    Examples:
      | strategy_id                       | action | price | symbol    | timestamp            | exchange | source      |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_FXS | buy    | 20    | FXSUSDT.P | 2024-02-11T04:01:51Z | BYBIT    | tradingview |
      | BTC_FEAR_GREED_INDEX_MOMENTUM_FXS | sell   | 20    | FXSUSDT.P | 2024-02-11T04:01:52Z | BYBIT    | tradingview |


#Scenario Outline: Filter duplicated alert
# Given There is an incoming aleırt,
#  When there is already same alert in alert_history table
#  Then it should record the alert and do not execute anything
#
#Scenario Outline: Handle BTC 0.001 and ETH 0.01 minimal bet issue in bybit
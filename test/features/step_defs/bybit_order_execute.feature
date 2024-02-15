# content of scenario_outlines.feature

Feature: Scenario outlines

  Scenario Outline: Outlined given, when, then
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples:
      | start | eat | left |
      | 12    | 5   | 7    |


#Scenario Outline: Filter duplicated alert
# Given There is an incoming alert,
#  When there is already same alert in alert_history table
#  Then it should record the alert and do not execute anything
#
#Scenario Outline: Handle BTC 0.001 and ETH 0.01 minimal bet issue in bybit
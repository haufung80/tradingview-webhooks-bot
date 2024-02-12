Feature: showing off behave

Scenario Outline: Blenders
   Given I put <thing> in a blender,
    When I switch the blender on
    Then it should transform into <other thing>

 Examples: Amphibians
   | thing         | other thing |
   | Red Tree Frog | mush        |

 Examples: Consumer Electronics
   | thing         | other thing |
   | iPhone        | toxic waste |
   | Galaxy Nexus  | toxic waste |

Scenario Outline: Filter duplicated alert
 Given There is an incoming alert,
  When there is already same alert in alert_history table
  Then it should record the alert and do not execute anything

Scenario Outline: Handle BTC 0.001 and ETH 0.01 minimal bet issue in bybit
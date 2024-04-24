![demopic](https://user-images.githubusercontent.com/38849824/160300853-ef6fe753-36d6-41a9-9bd2-8a06f7add71d.png)

![](https://img.shields.io/github/license/robswc/tradingview-webhooks-bot?style=for-the-badge)
![](https://img.shields.io/github/commit-activity/y/robswc/tradingview-webhooks-bot?style=for-the-badge)
![](https://img.shields.io/twitter/follow/robswc?style=for-the-badge)

[tvwb_demo.webm](https://user-images.githubusercontent.com/38849824/192352217-0bd08426-98b7-4188-8e5b-67d7aa93ba09.webm)

### 📀 Live Demo 🖥
**There's now a live demo available at [http://tvwb.robswc.me](http://tvwb.robswc.me).  
Feel free to check it out or send it some webhooks!**

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=2865cad8f863&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

### [Get Support on Discord](https://discord.gg/wrjuSaZCFh)


# The What 🔬

Tradingview-webhooks-bot (TVWB) is a small, Python-based framework that allows you to extend or implement your own logic
using data from [Tradingview's webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/). TVWB is not a trading library, it's a framework for building your own trading logic.

# The How 🏗

TVWB is fundamentally a set of components with a webapp serving as the GUI. TVWB was built with event-driven architecture in mind that provides you with the building blocks to extend or implement your own custom logic.
TVWB uses [Flask](https://flask.palletsprojects.com/en/2.2.x/) to handle the webhooks and provides you with a simple API to interact with the data.

# Quickstart 📘

### Installation

* [Docker](https://github.com/robswc/tradingview-webhooks-bot/wiki/Docker) (recommended)
* [Manual](https://github.com/robswc/tradingview-webhooks-bot/wiki/Installation)

### Hosting

* [Deploying](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting)
  * [Cloud](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting#cloud-hosting) (recommended)
  * [Local](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting#using-a-personal-pc)


---
Ensure you're in the `src` directory. When running the following commands, **if you installed manually**.  
**If you used docker**,
start the tvwb.py shell with `docker-compose run app shell` (in the project root directory) and omit the `python3 tvwb.py` portion of the commands.

---
### Creating an action

```bash
python3 tvwb.py action:create NewAction --register
```

This creates an action and automatically registers it with the app.  [Learn more on registering here](https://github.com/robswc/tradingview-webhooks-bot/wiki/Registering).

_Note, action and event names should **_always_** be in PascalCase._

You can also check out some "pre-made" [community actions](https://github.com/robswc/tradingview-webhooks-bot/tree/master/src/components/actions/community_created_actions)!

### Linking an action to an event

```bash
python3 tvwb.py action:link NewAction WebhookReceived
```

This links an action to the `WebhookReceived` event.  The `WebhookReceived` event is fired when a webhook is received by the app and is currently the only default event.

### Editing an action

Navigate to `src/components/actions/NewAction.py` and edit the `run` method.  You will see something similar to the following code.
Feel free to delete the "Custom run method" comment and replace it with your own logic.  Below is an example of how you can access
the webhook data.

```python
class NewAction(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Add your custom logic here.
        """
        data = self.validate_data()  # always get data from webhook by calling this method!
        print('Data from webhook:', data)
```

### Running the app

```bash
python3 tvwb.py start
```

### Sending a webhook

Navigate to `http://localhost:5000`.  Ensure you see the `WebhookReceived` Event.  Click "details" to expand the event box.
Find the "Key" field and note the value.  This is the key you will use to send a webhook to the app.  Copy the JSON data below,
replacing "YOUR_KEY_HERE" with the key you copied.

```json
{
    "key": "YOUR_KEY_HERE",
    "message": "I'm a webhook!"
}
```

The `key` field is required, as it both authenticates the webhook and tells the app which event to fire.  Besides that, you can
send any data you want.  The data will be available to your action via the `validate_data()` method. (see above, editing action)

On tradingview, create a new webhook with the above JSON data and send it to `http://ipaddr:5000/webhook`.  You should see the data from the webhook printed to the console.

### FAQs

#### So how do I actually trade?

To actually submit trades, you will have to use a library like [ccxt](https://github.com/ccxt/ccxt) for crypto currency.  For other brokers, usually there are 
SDKs or APIs available.  The general workflow would look something like: webhook signal -> tvwb (use ccxt here) -> broker.  Your trade submission would take place within the `run` method of a custom action.

#### The tvwb.py shell

You can use the `tvwb.py shell` command to open a python shell with the app context.  This allows you to interact with the app without having to enter `python3 tvwb.py` every time.

#### Running Docker on Windows/Mac?

Thanks to @khamarr3524 for pointing out there are some docker differences when running on Windows or Mac.  I've added OS-specific `docker-compose.yml` files to accomodate these differences.  One should be able to run their respective OS's `docker-compose.yml` file without issue now!

#### How do I get more help?

At the moment, the wiki is under construction.  However, you may still find some good info on there.  For additional assistance you can DM me on [Twitter](https://twitter.com/robswc) or join the [Discord](https://discord.gg/wrjuSaZCFh).  I will try my best to get back to you!

#### Command to create new event and register it, new action and register it  and link them together?

action:create FutuOrderExecute --register

event:create FutuWebhook --register

event:register FutuWebhook

action:link FutuOrderExecute FutuWebhook

#### SQLAlchemy ORM Migration

reference: https://dev.to/chrisjryan/database-migration-with-python-3gmg

### Order Execution Logic

#### Open position:

get the price from source, create limit order, create order history, update strategy active order

#### Close position:

first, check current position from order id, get execution details, update order history for the current position.

if the order is not filled:

1. cancel the order, create order history

if the order is filled:

1. create selling order, get selling order execution detail, create order history

if the order is partially filled:

1. cancel the order, create order history
2. create selling order, get selling order execution detail, create order history

### Deployment

#### I. Insert strategy from jupyter to dev DB

1. Copy the strategy from table, header as well
2. remove the parameter column
3. add a column of is_lev, determine if to use leverage or not
4. reformat the header as below

```bash
backtest_period,wfe,sr,l_sr,b_sr,win_rate,trd_num,sim_ret,lev_ret,bnh_ret,sim_mdd,lev_mdd,bnh_mdd,sim_add,lev_add,bnh_add,expos,leverage,position_size,strategy_id,strategy_name,direction,timeframe,symbol
```

4. import with following command

```bash
\copy public.strategy (backtest_period,wfe,sr,l_sr,b_sr,win_rate,trd_num,sim_ret,lev_ret,bnh_ret,sim_mdd,lev_mdd,bnh_mdd,sim_add,lev_add,bnh_add,expos,leverage,position_size,strategy_id,strategy_name,direction,timeframe,symbol) FROM '/Users/thfwork/Desktop/Algo Trading/tradingview-webhooks-bot/strategy_backup/strategy_bck.csv' CSV HEADER;
```

#### II. Create Alert in tradingview

1. modify strategy code accordingly for the strategy
2. add alert, enable webhook with URL pointing http://192.53.123.86/webhook
3. Message sample is as follow, Alert name is same as strategy_id

```bash
{
    "key": "BybitWebhook:xxxxx",
    "data": {
            "strategy_id": "SMA_CROSSOVER_LONG_1D_BTC",
            "action": "{{strategy.order.action}}",
            "price": "{{strategy.order.price}}",
            "timestamp": "{{timenow}}",
            "symbol": "{{ticker}}",
            "exchange": "{{exchange}}",
            "source": "tradingview",
            "position_size": "{{strategy.position_size}}",
            "noofcontracts": "{{strategy.order.contracts}}",
            "orderid": "{{strategy.order.id}}",
            "comment": "{{strategy.order.comment}}",
            "alert_msg": "{{strategy.order.alert_message}}",
            "market_position": "{{strategy.market_position}}",
            "market_position_size": "{{strategy.market_position_size}}",
            "prev_market_position": "{{strategy.prev_market_position}}",
            "prev_market_position_size": "{{strategy.prev_market_position_size}}"
        }
}
```

#### III. Strategy deployment

1. Set Strategy as Active, Config Strategy to use personal_acc

```bash
update strategy set active = true where strategy_name in (
'MACD_CROSSOVER_LONG_1D'
);
update strategy set personal_acc = true where symbol in ('STETH', 'XEC', 'ONE', 'TRU', 'QI', 'NEO', 'WBTC', 'HNT', 'VET', 'WEMIX', 'CRO', 'SC', 'ROSE', 'QNT', 'KCS');
```

3. export the table from production to /strategy_backup/strategy_{yyyymmdd}.csv
4. pull and make change in local for same files
5. (run SQLAlchemy ORM Migration if there is schema change)
6. push to prod
7. run command

```bash
psql 'postgresql://postgres:XXXX@localhost/tradingview-webhooks-bot'
delete from strategy; \g
\copy strategy from '/root/Desktop/tradingview-webhooks-bot/strategy_backup/strategy_bck.csv' delimiter ',' CSV HEADER;
```

6. Allocate fund in strategy_management

```bash
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  100, 100, 'BYBIT', true from strategy where symbol in ('WBTC','STETH','BTC', 'ETH', 'SOL') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  300, 300, 'BITGET', true from strategy where symbol in ('WBTC','STETH','BTC', 'ETH', 'SOL') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  100, 100, 'OKEX', true from strategy where symbol in ('WBTC','STETH','BTC', 'ETH', 'SOL') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  0, 0, 'BYBIT', true from strategy where symbol in ('OKB','LEO') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  0, 0, 'BITGET', false from strategy where symbol in ('OKB','LEO') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  300, 300, 'OKEX', false from strategy where symbol in ('OKB','LEO') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  0, 0, 'BYBIT', false from strategy where symbol in ('GNO','OSMO','RIF') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  300, 300, 'BITGET', true from strategy where symbol in ('GNO','OSMO','RIF') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  0, 0, 'OKEX', false from strategy where symbol in ('GNO','OSMO','RIF') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  300, 300, 'BYBIT', true from strategy where symbol in ('QI', 'KCS', 'XMR') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  0, 0, 'BITGET', false from strategy where symbol in ('QI', 'KCS', 'XMR') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  0, 0, 'OKEX', false from strategy where symbol in ('QI', 'KCS', 'XMR') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  150, 150, 'BYBIT', true from strategy where symbol in ('JASMY','TRU', 'KAVA', 'SEI', 'HNT', 'VET', 'WEMIX', 'RUNE', 'CAKE', 'ROSE', 'QNT') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  150, 150, 'BITGET', true from strategy where symbol in ('JASMY','TRU', 'KAVA', 'SEI', 'HNT', 'VET', 'WEMIX', 'RUNE', 'CAKE', 'ROSE', 'QNT') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  0, 0, 'OKEX', false from strategy where symbol in ('JASMY','TRU', 'KAVA', 'SEI', 'HNT', 'VET', 'WEMIX', 'RUNE', 'CAKE', 'ROSE', 'QNT') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  150, 150, 'BYBIT', true from strategy where symbol in ('SC') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  0, 0, 'BITGET', false from strategy where symbol in ('SC') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  150, 150, 'OKEX', true from strategy where symbol in ('SC') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  0, 0, 'BYBIT', false from strategy where symbol in ('RAY') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false, 150, 150, 'BITGET', true from strategy where symbol in ('RAY') and strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  150, 150, 'OKEX', true from strategy where symbol in ('RAY') and (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));

insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BYBIT'), strategy_id, false,  100, 100, 'BYBIT', true from strategy where strategy_id not in (select strategy_id from strategy_management where exchange = 'BYBIT'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_BITGET'), strategy_id, false,  100, 100, 'BITGET', true from strategy where strategy_id not in (select strategy_id from strategy_management where exchange = 'BITGET'));
insert into strategy_management(strat_mgmt_id, strategy_id, active_order, fund, init_fund, exchange, active) (select concat(strategy_id,'_OKEX'), strategy_id, false,  100, 100, 'OKEX', true from strategy where (direction = 'long' or direction = 'LONG') and strategy_id not in (select strategy_id from strategy_management where exchange = 'OKEX'));
```

#### Code deployment

1. push change to prod
2. kill the cmd and run startup.sh

#### DB schema deployment

1. modify ./src/model/model.py
2. generate a change file

```bash
alembic revision --autogenerate -m "commit message"
```

4. (PLEASE CHECK THE CHANGE FILE BEFORE PROCEED)
5. update database

```bash
alembic upgrade head
```

7. push change to prod
8. kill the cmd and run startup.sh

### Fund deployment

#### Possible Max Drawdown of my account

```bash
select exchange, sum(sm.init_fund*(-sim_mdd/100)) from strategy s, strategy_management sm where s.strategy_id = sm.strategy_id and sim_mdd is not null group by exchange;
select s.personal_acc, sum(sm.init_fund*(-sim_mdd/100)) from strategy s, strategy_management sm where s.strategy_id = sm.strategy_id and exchange = 'BYBIT' and sim_mdd is not null group by personal_acc;
```

#### Required fund for my account

```bash
select exchange, sum(sm.fund*position_size*(expos/100)) from strategy s, strategy_management sm where s.strategy_id = sm.strategy_id and sim_mdd is not null group by exchange;
select s.personal_acc, sum(sm.init_fund*(-sim_mdd/100)) from strategy s, strategy_management sm where s.strategy_id = sm.strategy_id and exchange = 'BYBIT' and sim_mdd is not null group by personal_acc;
```

#### run test

thfwork@TangdeMBP features % pytest --html=report.html

#### check debug log

1. error is output to a txt in server

2. Useful DB query

```bash
select timestamp, o.exchange, strategy_id, action, price, symbol, error, error_stack, message_payload from alert_history a, order_execution_error o where a.id = o.alert_id and source = 'tradingview' order by a.id desc
```

```bash	
delete from strategy_management where strategy_id in ('MACD_CROSSOVER_4H_APT',
'MACD_CROSSOVER_4H_WLD')
```

```bash
select distinct(s.strategy_id) from strategy s, strategy_management sm where s.strategy_id = sm.strategy_id and (
	strategy_name in ('SMA_CROSSOVER',
'BOLL_BAND_MOMENTUM' ,
'BOLL_BAND_REVERSION' ,
'BTC_SOPR_MOMENTUM' ,
'MACD_CROSSOVER' ,
'BTC_FEAR_GREED_INDEX_MOMENTUM',
'STOCH_OSCILL_MOMENTUM',
'SMA_CROSSOVER_4H',
'BOLL_BAND_MOMENTUM_4H',
'STOCH_OSCILL_MOMENTUM_4H',
'BOLL_BAND_REVERSION_4H',
'MACD_CROSSOVER_4H') or 
s.strategy_id in ('STOCH_OSCILL_MOMENTUM_LONG_1D_MKR',
'MACD_CROSSOVER_SHORT_4H_BCH')) and active_order = false and exchange = 'BYBIT'
```

select distinct(strategy_id) from strategy_management where active_order = false and strategy_id in (
'MACD_CROSSOVER_LONG_1D_VET',
'SMA_CROSSOVER_LONG_4H_FET',
'SMA_CROSSOVER_LONG_4H_WBTC',
'SMA_CROSSOVER_LONG_1D_WBTC',
'STOCH_OSCILL_MOMENTUM_LONG_4H_AGIX',
'STOCH_OSCILL_MOMENTUM_LONG_4H_FET',
'STOCH_OSCILL_MOMENTUM_LONG_4H_FIL',
'STOCH_OSCILL_MOMENTUM_LONG_4H_ONE',
'BOLL_BAND_REVERSION_LONG_4H_MATIC',
'MACD_CROSSOVER_LONG_4H_FIL',
'MACD_CROSSOVER_LONG_4H_GRT') order by strategy_id desc

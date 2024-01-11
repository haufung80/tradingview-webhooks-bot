#!/bin/sh
cd ~/Desktop/tradingview-webhooks-bot/src
git pull
pip install -r requirements.txt --break-system-packages
alembic upgrade head
python3 tvwb.py start
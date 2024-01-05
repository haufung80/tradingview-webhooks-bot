#!/bin/sh
cd ~/Desktop/tradingview-webhooks-bot/src
pip install -r requirements.txt --break-system-packages
python3 tvwb.py start
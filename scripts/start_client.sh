#!/usr/bin/bash
git pull
pip3 install -U -r requirements.txt

cd src/
python3 bot.py

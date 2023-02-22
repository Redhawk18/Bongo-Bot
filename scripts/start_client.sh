#!/usr/bin/bash
git pull
pip3 install -U -r requirements.txt

python3 ../src/main.py

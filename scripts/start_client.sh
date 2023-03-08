#!/usr/bin/bash
cd $( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
cd ..

git pull
pip3 install -U -r requirements.txt

python3 src/main.py

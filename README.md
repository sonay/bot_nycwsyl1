# bot_nycwsyl1

## Purpose

bot_nycwsyl1 is a scrapper to parse [New York Times Mini Game](https://www.nytimes.com/crosswords/game/mini)
into a json file. Because a unique identifier for the result is created on each run, exact name of the json
file can be extracted/viewed from the bot_nycwsyl1.log with a loglevel INFO.

It also outputs a human-readable parse result to stdout.

## How to build

```
python3 -m venv venv-bot_nycwsyl1
source venv-bot_nycwsyl1/bin/activate
pip3 install -r requirements.txt 
```

## How to run
```
python3 main.py 
```

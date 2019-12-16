import time
import requests
import json
import datetime

def load_config():
    try:
        with open("res/config.json", encoding="utf-8") as fil:
            return json.load(fil)
    except IOError as e:
        return None

def auth(method): 
    data = load_config()
    if data == None: return None
    else: return {"Authorization": data["token"], "Content-Type": "application/json", "method": method.upper()}

api_url = "https://discordapp.com/api/v6"

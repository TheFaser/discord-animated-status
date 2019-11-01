import time
import requests
import asyncio
import threading
import json

def load_config():
    with open("res/config.txt") as json_file:
        data = json.load(json_file)
    return data

def changer():
    while True:
        for frame in data["frames"]:
            p_headers = {"Authorization": token, "Content-Type": "application/json", "method": "PATCH"}
            s_params = {"custom_status": {"text": frame, "emoji_id": None, "emoji_name": None, "expires_at": None}}
            p_params = json.dumps(s_params)
            req = requests.patch("https://discordapp.com/api/v6/users/@me/settings", headers=p_headers, data=p_params)
            print("Switched frame to: %s" % frame)
            time.sleep(3)

data = load_config()
token = data["token"]

def entry():
    while True:
        changer()

if __name__ == '__main__':
    entry()


__author__ = "https://github.com/eternalfrenzy | https://vk.com/eternalfrenzy"

import time
import requests
import json
from frameparser import *

def load_config():
    with open("res/config.json") as fil:
        return json.load(fil)

def changer():
    data = load_config()
    for frame in data["frames"]:
        frame = parse_frame(frame)
        p_headers = {"Authorization": data["token"], "Content-Type": "application/json", "method": "PATCH"}
        p_params = json.dumps({"custom_status": {"text": frame["str"], "emoji_id": None, "emoji_name": frame["emoji"], "expires_at": None}})
        requests.patch("https://discordapp.com/api/v6/users/@me/settings", headers=p_headers, data=p_params)
        print("Switched frame to: %s" % frame["str"])
        time.sleep(3)

def entry():
    while True:
        changer()

if __name__ == '__main__':
    entry()

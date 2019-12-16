
__author__  = "https://github.com/eternalfrenzy | https://vk.com/eternalfrenzy"
__version__ = 1.3

from frameparser import *

def changer():
    data = load_config()
    if data == None: return False
    for frame in data["frames"]:
        frame = parse_frame(frame)
        try:
            p_params = json.dumps({"custom_status": {"text": frame["str"], "emoji_id": None, "emoji_name": frame["emoji"], "expires_at": None}})
        except KeyError as e:
            print("Unable to create request params: \n%s" % e)
        try:
            requests.patch(api_url+"/users/@me/settings", headers=auth("patch"), data=p_params)
            print("Switched frame to: %s" % frame["str"])
        except requests.exceptions.RequestException as e:
            print("Unable to send request to discord: \n%s" % e)
        try:
            time.sleep(data["speed"])
        except KeyError as e:
            print("Unable to delay the iteration: \n%s" % e)

def entry():
    while True:
        changer()

if __name__ == '__main__':
    entry()

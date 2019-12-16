from required import *

def parse_frame(frame):
    now = datetime.datetime.now()
    frame["str"] = frame["str"].replace("#curtime#", datetime.datetime.strftime(now, "%H:%M"))
    frame["str"] = frame["str"].replace("#servcount#", str(len(requests.get(api_url+"/users/@me/guilds", headers=auth("get")).json(encoding="utf-8"))))
    return frame
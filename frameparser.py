import datetime

def parse_frame(frame):
    now = datetime.datetime.now()
    time = datetime.datetime.strftime(now, "%H:%M")
    frame["str"] = frame["str"].replace("#curtime#", time)
    return frame
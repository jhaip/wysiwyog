import logging
import sys
import RPCClient
import time
import json
import requests

M = RPCClient.RPCClient()
id = sys.argv[1]
CAM_WIDTH = 1920
CAM_HEIGHT = 1080

time.sleep(1)
M.when_set_filter("CLAIM[global/papers]")
M.when_set_filter("CLAIM[global/dots]")

def claim(s):
    payload = {"facts": s}
    logging.error("POSTING")
    # logging.error(payload)
    r = requests.post("http://localhost:3000/assert", data=payload)
    logging.error(r.text)
    return r

def retract(s):
    payload = {"facts": s}
    logging.error("RETRACT")
    r = requests.post("http://localhost:3000/retract", data=payload)
    logging.error(r.text)
    return r

def transform_dot(dot):
    return {
        "x": dot["x"] * 1.0 / CAM_WIDTH,
        "y": dot["y"] * 1.0 / CAM_HEIGHT,
        "r": dot["color"][0],
        "g": dot["color"][1],
        "b": dot["color"][2]
    }

while True:
    string = M.when_recv()
    msg_prefix = string.split("]", 1)[0]
    msg = string.split("]", 1)[1]
    val = json.loads(msg)
    if "papers" in msg_prefix:
        papers = val
        papers_str = json.dumps(papers).replace("\"", "'")
        millis = int(round(time.time() * 1000))
        retract("camera $ sees papers $ @ $")
        claim("camera {0} sees papers \"{1}\" @ {2}".format(1, papers_str, millis))
    elif "dots" in msg_prefix:
        dots = val
        new_dots = list(map(transform_dot, dots))
        dot_str = json.dumps(new_dots).replace("\"", "'")
        millis = int(round(time.time() * 1000))
        # retract("camera $ sees dots $ @ $")
        # claim("camera {0} sees dots \"{1}\" @ {2}".format(1, dot_str, millis))

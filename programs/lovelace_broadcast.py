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
LOVELACE_URL = "http://10.0.0.162:3000"

time.sleep(1)
M.when_set_filter("CLAIM[global/papers]")
M.when_set_filter("CLAIM[global/dots]")

def claim(s):
    payload = {"facts": s}
    logging.error("POSTING")
    # logging.error(payload)
    r = requests.post(LOVELACE_URL + "/assert", data=payload)
    logging.error(r.text)
    return r

def retract(s):
    payload = {"facts": s}
    logging.error("RETRACT")
    r = requests.post(LOVELACE_URL + "/retract", data=payload)
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
        retract("camera $ sees papers $ @ $")
        millis = int(round(time.time() * 1000))
        # papers_str = json.dumps(papers).replace("\"", "'")
        # claim("camera {0} sees papers \"{1}\" @ {2}".format(1, papers_str, millis))
        papers_facts = []
        for paper in papers:
            papers_facts.append("camera {} sees paper {} at TL ({}, {}) TR ({}, {}) BR ({}, {}) BL ({}, {}) @ ({}, {})".format(
                1,
                paper["id"],
                paper["corners"][0]["x"], paper["corners"][0]["y"],
                paper["corners"][1]["x"], paper["corners"][1]["y"],
                paper["corners"][2]["x"], paper["corners"][2]["y"],
                paper["corners"][3]["x"], paper["corners"][3]["y"],
                millis))
        claim(papers_facts)
    elif "dots" in msg_prefix:
        dots = val
        new_dots = list(map(transform_dot, dots))
        dot_str = json.dumps(new_dots).replace("\"", "'")
        millis = int(round(time.time() * 1000))
        # retract("camera $ sees dots $ @ $")
        # claim("camera {0} sees dots \"{1}\" @ {2}".format(1, dot_str, millis))

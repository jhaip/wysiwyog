import logging
import sys
import RPCClient
import time
import json
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

request_session = requests.Session()

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ],
                raise_on_redirect=False,
                raise_on_status=False)

request_session.mount('http://', HTTPAdapter(max_retries=retries))

M = RPCClient.RPCClient()
id = sys.argv[1]
CAM_WIDTH = 1920
CAM_HEIGHT = 1080
LOVELACE_URL = "http://localhost:3000"
MSG_PREFIX = '#' + id + ' '

time.sleep(1)
M.when_set_filter("CLAIM[global/papers]")
M.when_set_filter("CLAIM[global/dots]")
M.when_set_filter("CLAIM[global/projector_calibration]")

def claim(s):
    payload = {"facts": s}
    logging.error("POSTING")
    # logging.error(payload)
    r = request_session.post(LOVELACE_URL + "/assert", data=payload)
    logging.error(r.text)
    return r

def retract(s):
    payload = {"facts": s}
    logging.error("RETRACT")
    r = request_session.post(LOVELACE_URL + "/retract", data=payload)
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
        retract(MSG_PREFIX + "camera 1 sees paper $ at TL ($, $) TR ($, $) BR ($, $) BL ($, $) @ $")
        retract(MSG_PREFIX + "camera 1 sees no papers @ $")
        millis = int(round(time.time() * 1000))
        # papers_str = json.dumps(papers).replace("\"", "'")
        # claim("{}camera {0} sees papers \"{1}\" @ {2}".format(MSG_PREFIX, 1, papers_str, millis))
        papers_facts = []
        for paper in papers:
            papers_facts.append("{}camera 1 sees paper {} at TL ({}, {}) TR ({}, {}) BR ({}, {}) BL ({}, {}) @ {}".format(
                MSG_PREFIX,
                paper["id"],
                paper["corners"][0]["x"], paper["corners"][0]["y"],
                paper["corners"][1]["x"], paper["corners"][1]["y"],
                paper["corners"][2]["x"], paper["corners"][2]["y"],
                paper["corners"][3]["x"], paper["corners"][3]["y"],
                millis))
        if len(papers) is 0:
            papers_facts.append("{}camera 1 sees no papers @ {}".format(MSG_PREFIX, millis))
        claim(papers_facts)
    elif "dots" in msg_prefix:
        dots = val
        new_dots = list(map(transform_dot, dots))
        dot_str = json.dumps(new_dots).replace("\"", "'")
        millis = int(round(time.time() * 1000))
        # retract(MSG_PREFIX + "camera $ sees dots $ @ $")
        # claim("{}camera {0} sees dots \"{1}\" @ {2}".format(MSG_PREFIX, 1, dot_str, millis))
    elif "projector_calibration" in msg_prefix:
        projector_calibration = val
        retract("$ camera 1 has projector calibration TL ($, $) TR ($, $) BR ($, $) BL ($, $) @ $")
        if projector_calibration and len(projector_calibration) is 4:
            millis = int(round(time.time() * 1000))
            claim("{}camera 1 has projector calibration TL ({}, {}) TR ({}, {}) BR ({}, {}) BL ({}, {}) @ {}".format(
                MSG_PREFIX,
                projector_calibration[0][0],
                projector_calibration[0][1],
                projector_calibration[1][0],
                projector_calibration[1][1],
                projector_calibration[2][0],
                projector_calibration[2][1],
                projector_calibration[3][0],
                projector_calibration[3][1],
                millis))

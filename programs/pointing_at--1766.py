import logging
import sys
import RPCClient
import json
import time
import math

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[global/papers]")
paper_im_pointing_at = None
WISKER_LENGTH = 150

while True:
    string = M.when_recv()
    event_type = string.split('[', 1)[0]  # WISH, CLAIM
    msg_prefix = string.split(']', 1)[0] + "]"
    val = json.loads(string[len(msg_prefix):])
    if "papers" in msg_prefix:
        papers = val
        point_im_pointing_at = M.get_paper_you_point_at(papers, id, WISKER_LENGTH)
        M.draw_wisker(papers, id, WISKER_LENGTH)

        # Draw a label of what I'm pointing at
        ill = M.new_illumination(id)
        ill.fontsize(40)
        ill.fontcolor(100, 255, 255)
        if point_im_pointing_at is not None:
            ill.text(str(point_im_pointing_at), 10, 10)
        else:
            ill.text("None", 10, 10)
        M.wish("DRAW", id, ill.package())

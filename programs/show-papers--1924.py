import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()
id = sys.argv[1]
time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[global/papers]")

while True:
    string = M.when_recv()
    msg_prefix = string.split(']', 1)[0] + "]"
    papers = json.loads(string[len(msg_prefix):])
    ill = M.new_illumination("global")
    ill.fill(0, 255, 0, 99)
    for paper in papers:
        if len(paper["corners"]) == 4:
            tri1 = []
            tri2 = []
            for corner in paper["corners"]:
                if corner["CornerId"] in [0,1,2]:
                    tri1.append(corner)
                if corner["CornerId"] in [2,3,0]:
                    tri2.append(corner)
            ill.polygon(list(map(lambda c: (c["x"], c["y"]), tri1)))
            ill.polygon(list(map(lambda c: (c["x"], c["y"]), tri2)))
    M.wish("DRAW", id, ill.package())

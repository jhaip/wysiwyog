import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()
id = sys.argv[1]
time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[global/dots]")

while True:
    string = M.when_recv()
    msg_prefix = string.split(']', 1)[0] + "]"
    dots = json.loads(string[len(msg_prefix):])
    ill = M.new_illumination("global")
    for dot in dots:
        ill.fill(dot["color"][0], dot["color"][1], dot["color"][2])
        ill.stroke(255, 255, 0)
        s = 3
        ill.ellipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)
    M.wish("DRAW", id, ill.package())

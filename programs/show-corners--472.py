import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()
id = sys.argv[1]
time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[global/corners]")

while True:
    string = M.when_recv()
    msg_prefix = string.split(']', 1)[0] + "]"
    corners = json.loads(string[len(msg_prefix):])
    ill = M.new_illumination("global")

    for corner in corners:
        ill.fontcolor(255, 0, 0)
        ill.text(corner["colorString"], corner["corner"]["x"], corner["corner"]["y"]+20)
        step = 10
        s = 3
        for i, c in enumerate(corner["colorString"]):
            raw_color = corner["rawColorsList"][i]
            ill.fill(*raw_color)
            ill.ellipse(corner["corner"]["x"]+i*step-s, corner["corner"]["y"]-s, s*2, s*2)
            if c == '0':
                ill.fill(255, 0, 0)
            elif c == '1':
                ill.fill(0, 255, 0)
            elif c == '2':
                ill.fill(0, 0, 255)
            elif c == '3':
                ill.fill(200, 200, 200)
            ill.ellipse(corner["corner"]["x"]+i*step-s, corner["corner"]["y"]+10-s, s*2, s*2)
    M.wish("DRAW", id, ill.package())

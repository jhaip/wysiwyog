import logging
import sys
import RPCClient
import json

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

ill = M.new_illumination(id)
ill.translate(10, 0)
ill.text("OOYEAH", 40, 40)
ill.rectangle(20, 20, 10, 10)
ill.line(40, 20, 40, 30)
ill.nofill()
ill.ellipse(20, 60, 40, 10)
ill.rotate(0.1)
ill.fontsize(50)
ill.fontcolor(255, 0, 0)
ill.text("hey you", 20, 80)

M.wish("DRAW", id, ill.package())
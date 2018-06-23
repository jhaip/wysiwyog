import logging
import datetime
import RPCClient
import time
import sys

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

time.sleep(1)  # wait for other programs to acknowledge it as a pub source

time_str = str(datetime.datetime.now().strftime("%H : %M : %S"))
M.claim("paper1", "time", time_str)

ill = M.new_illumination(id)
ill.rotate(3.14/2.0)
ill.fontsize(20)
ill.text(time_str, 10, -60)
M.wish("DRAW", id, ill.package())

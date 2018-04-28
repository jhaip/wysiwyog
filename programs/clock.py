import logging
import datetime
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

while True:
    time_str = str(datetime.datetime.now())
    logging.info("tick %s" % time_str)
    M.claim("clock", "time", time_str)
    time.sleep(1)

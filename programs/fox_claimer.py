import logging
import sys
import RPCClient
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

time.sleep(1)
# wait for a second for subscribers to be notified
# of the socket subscription before sending data.
# TODO: figure out how to make this not needed

id = sys.argv[1]
M.claim(str(id), "fox", "out")

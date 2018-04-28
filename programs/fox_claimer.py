import logging
import sys
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]
M.claim(id, "fox", "out")

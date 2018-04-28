import logging
import datetime
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

M.claim("paper1", "time", str(datetime.datetime.now()))

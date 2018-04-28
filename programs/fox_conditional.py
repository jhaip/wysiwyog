import logging
import sys
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]


def when_fox(fox):
    logging.info("Inside when fox")
    if fox == "out":
        M.wish("DRAW", id, "The fox is out!")


M.when(4, "fox", when_fox)

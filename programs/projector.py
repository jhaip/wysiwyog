import time
import logging
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

while True:
    wishes = M.get_wishes_by_type("DRAW")
    result = {}
    for wish in wishes:
        result[wish.source] = result.get(wish.source, '') + wish.action
    logging.info(result)
    M.clear_wishes({"type": "DRAW"})

    time.sleep(1)

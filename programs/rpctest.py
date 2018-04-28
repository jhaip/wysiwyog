import logging
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()


logging.info("get_wishes_by_type")
logging.info(M.get_wishes_by_type("DRAW"))

logging.info("clear_wishes")
logging.info(M.clear_wishes({"type": "DRAW"}))

logging.info("wish")
logging.info(M.wish("DRAW", "SOURCE", "ACTION"))

logging.info("claim")
logging.info(M.claim("SOURCE", "KEY", "VALUE"))

logging.info("when")

M.when("SOURCE", "KEY", lambda d: logging.info(d))

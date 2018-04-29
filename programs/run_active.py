import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

while True:
    # M.stop_program(1)
    # M.stop_program(2)
    # M.stop_program(3)
    # M.stop_program(4)
    # M.run_program(1)
    # M.run_program(2)
    M.run_program(3)
    # M.run_program(4)
    # M.run_program(5)
    # M.run_program(6)

    time.sleep(1)

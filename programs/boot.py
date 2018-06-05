import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

time.sleep(1)  # HACK: wait a sec for master to initialize

M.run_program(7)  # Run active papers
M.run_program(8)  # HTTP RPC
M.run_program(99)  # Code mgmt test

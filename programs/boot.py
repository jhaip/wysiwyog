import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

time.sleep(1)  # HACK: wait a sec for master to initialize

M.add_program(1, "/app/programs/one_tick.py")
M.add_program(2, "/app/programs/clock.py")
M.add_program(1072, "/app/programs/drawer1.py")
M.add_program(1054, "/app/programs/fox_claimer.py")
M.add_program(1688, "/app/programs/fox_conditional.py")
M.add_program(6, "/app/programs/projector.py")
M.add_program(7, "/app/programs/run_papers.py")

M.run_program(7)

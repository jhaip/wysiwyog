import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

program_id = M.create_program("test_1")["id"]

logging.error("Program id:")
logging.error(program_id)

def on_get_code(val):
    if val == "":
        logging.error("CODE MATCHES")
    else:
        logging.error("CODE - VALUE ERROR!")
        logging.error(val)

M.when("code", program_id, on_get_code)

M.run_program(program_id)
time.sleep(1)

code_v1 = """
import sys
import RPCClient

M = RPCClient.RPCClient()
id = sys.argv[1]
M.claim(id, "test_1_claim", "test_1_claim_1")
"""
M.update_program(program_id, code_v1)

M.run_program(program_id, restart=True)
time.sleep(1)

def on_when(val):
    if val == "test_1_claim_1":
        logging.error("TEST CLAIM 1 - ok")
    else:
        logging.error("TEST CLAIM 1 - VALUE ERROR!")
        logging.error(val)

M.when(program_id, "test_1_claim", on_when)

code_v2 = """
import sys
import RPCClient

M = RPCClient.RPCClient()
id = sys.argv[1]
M.claim(id, "test_1_claim", "test_1_claim_2")
"""
M.update_program(program_id, code_v2)

M.run_program(program_id, restart=True)
time.sleep(1)

def on_when(val):
    if val == "test_1_claim_2":
        logging.error("TEST CLAIM 2 - ok")
    else:
        logging.error("TEST CLAIM 2 - VALUE ERROR!")
        logging.error(val)

M.when(program_id, "test_1_claim", on_when)

M.stop_program(program_id)

logging.error("DONE with test")

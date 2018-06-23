import logging
import sys
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

M.when_set_filter("CLAIM[1054/fox]")
M.when_set_filter("DEATH[1054]")

while True:
    string = M.when_recv()
    event_type = string.split('[', 1)[0]  # CLAIM, DEATH, WISH
    fox = None
    if event_type == "DEATH":
        fox = None
    elif event_type == "CLAIM":
        fox = string[len("CLAIM[1054/fox]"):]
        logging.error(fox)
    ill = M.new_illumination(id)
    # "\"out\"" is used because it equals json.dumps("out")
    # TODO: change RPCClient to not encode pure text as json
    if fox == "\"out\"":
        ill.text("The fox is out!", 40, 40)
    else:
        ill.text("Where is Mr. fox?", 10, 10)
    M.wish("DRAW", id, ill.package())

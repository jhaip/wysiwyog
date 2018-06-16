import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

M.clear_wishes({"source": str(id)})

text_cache = ""
last_key_id = None

while True:
    def when_keys(keys):
        global text_cache, last_key_id
        if keys:
            if last_key_id is None:
                # Intial case. Catch up to lastest id but ignore cached text
                last_key_id = keys[-1]["id"]
                return
            for d in keys:
                if d["id"] > last_key_id:
                    last_key_id = d["id"]
                    if d["key"]:
                        text_cache += d["key"]
                    if d["special_key"]:
                        special_key_map = {
                            "enter": "\n",
                            "space": " ",
                            "tab": "\t"
                        }
                        if d["special_key"] in special_key_map:
                            text_cache += special_key_map[d["special_key"]]
                        elif d["special_key"] == "backspace":
                            text_cache = text_cache[:-1]
            ill = M.new_illumination("global")
            ill.fontsize(16)
            ill.text(text_cache, 20, 20)
            M.wish("DRAW", id, ill.package())

    KEYBOARD_PROGRAM_ID = 500
    M.when(KEYBOARD_PROGRAM_ID, "keys", when_keys)

    time.sleep(0.01)

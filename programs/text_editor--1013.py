import logging
import sys
import RPCClient
import json
import time
import uuid

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

M.clear_wishes({"source": str(id)})

text_cache = "ABCDEFGHIJ\nKLMNopqrstu\nvwyz.123"
last_key_id = None
cursor_index = 0
cursor_position = [0, 0]
KEYBOARD_PROGRAM_ID = 500
program_id = 670
editor_program_state = "NOT_LOADED"
editor_program_req_id = None

def insert_str(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]

def remove_char(string, index):
    return string[:index] + string[index+1:]

def get_cursor_position(string, index):
    text_before = string[:index]
    y = text_before.count("\n")
    index_of_last_newline = text_before.rfind("\n")
    x = 0
    if index_of_last_newline == -1:
        x = index
    else:
        x = index - index_of_last_newline - 1
    return (x, y)

def get_cursor_index_from_position(string, position):
    lines = string.split("\n")
    OUT_OF_BOUNDS = None
    if position[1] < 0 or position[1] > len(lines) - 1:
        return OUT_OF_BOUNDS
    if position[0] < 0 or position[0] > len(lines[position[1]]):
        return OUT_OF_BOUNDS
    index = 0
    for i in range(position[1]):
        index += len(lines[i]) + 1
    index += position[0]
    return index

def get_position_for_end_of_line(string, y):
    lines = string.split("\n")
    return len(lines[y])

def get_line_count(string):
    return len(string.split("\n"))

def handle_key_update(keys):
    global text_cache, last_key_id, cursor_index, cursor_position, KEYBOARD_PROGRAM_ID
    if keys:
        if last_key_id is None:
            # Intial case. Catch up to lastest id but ignore cached text
            last_key_id = keys[-1]["id"]
            return
        for d in keys:
            if d["id"] > last_key_id:
                last_key_id = d["id"]
                if d["key"]:
                    text_cache = insert_str(text_cache, d["key"], cursor_index)
                    cursor_index += 1
                    cursor_position[0] += 1
                if d["special_key"]:
                    special_key_map = {
                        "enter": "\n",
                        "space": " ",
                        "tab": "\t"
                    }
                    logging.error(d["special_key"])
                    if d["special_key"] in special_key_map:
                        new_char = special_key_map[d["special_key"]]
                        text_cache = insert_str(text_cache, new_char, cursor_index)
                        cursor_index += 1
                        if new_char == "\n":
                            cursor_position[0] = 0
                            cursor_position[1] += 1
                        else:
                            cursor_position[0] += 1
                    elif d["special_key"] == "backspace":
                        if cursor_index > 0:
                            char_to_be_removed = text_cache[cursor_index - 1]
                            text_cache = remove_char(text_cache, cursor_index - 1)
                            cursor_index -= 1
                            if char_to_be_removed == "\n":
                                cursor_position[0] = get_cursor_position(text_cache, cursor_index)[0]
                                cursor_position[1] -= 1
                            else:
                                cursor_position[0] -= 1
                    elif d["special_key"] == "up":
                        if cursor_position[1] > 0:
                            cursor_position[1] = cursor_position[1] - 1
                            new_cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                            if new_cursor_index is None:
                                cursor_position[0] = get_position_for_end_of_line(text_cache, cursor_position[1])
                            cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                    elif d["special_key"] == "down":
                        if cursor_position[1] < get_line_count(text_cache) - 1:
                            cursor_position[1] = cursor_position[1] + 1
                            new_cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                            if new_cursor_index is None:
                                cursor_position[0] = get_position_for_end_of_line(text_cache, cursor_position[1])
                            cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                    elif d["special_key"] == "right":
                        cursor_position[0] = cursor_position[0] + 1
                        new_cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                        if new_cursor_index is None:
                            cursor_position[0] = cursor_position[0] - 1
                        cursor_index = get_cursor_index_from_position(text_cache, cursor_position)
                    elif d["special_key"] == "left":
                        if cursor_position[0] > 0:
                            cursor_position[0] = cursor_position[0] - 1
        draw()


def draw():
    global text_cache, cursor_index, cursor_position
    font_size = 15
    char_width = font_size * 0.6
    char_height = font_size * 1.3
    origin = (12, 8)
    ill = M.new_illumination(id)
    ill.fontsize(font_size)
    ill.text(text_cache, origin[0], origin[1])
    ill.nostroke()
    ill.fill(255, 0, 0, 100)
    cursor_x = origin[0] + char_width * cursor_position[0]
    cursor_y = origin[1] + char_height * cursor_position[1]
    ill.rectangle(cursor_x, cursor_y, char_width, char_height)
    M.wish("DRAW", id, ill.package())


time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[{0}/keys]".format(KEYBOARD_PROGRAM_ID))

while True:
    if editor_program_state == "NOT_LOADED":
        req_id = str(uuid.uuid4())
        req = {
            "name": "source_code",
            "options": {"id": program_id},
            "request_id": req_id
        }
        editor_program_req_id = req_id
        M.when_set_filter("CLAIM[RECLAIM/{0}]".format(req_id))
        editor_program_state = "WAITING_FOR_CODE"
        M.wish("RECLAIM", id, json.dumps(req))
        logging.error("WAITING FOR CODE")

    logging.error("WAITING to recv")
    string = M.when_recv()
    event_type = string.split('[', 1)[0]  # WISH, CLAIM
    # Either "CLAIM[RECLAIM/XXXX...]" or "CLAIM[XXXX/keys]"
    msg_prefix = string.split(']', 1)[0] + "]"
    val = json.loads(string[len(msg_prefix):])
    if "RECLAIM" in msg_prefix:
        editor_program_req_id = None
        M.when_clear_filter(msg_prefix)
        logging.error("GOT code!")
        logging.error(val)
        if "error" in val:
            logging.error("Error in response to get code")
            logging.error(val["error"])
            editor_program_state = "ERROR"
        else:
            text_cache = val["code"]
            editor_program_state = "LOADED"
            draw()
    elif "keys" in msg_prefix:
        logging.error("handilng key update")
        keys = val
        handle_key_update(keys)

    time.sleep(0.01)

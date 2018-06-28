import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

M.clear_wishes({"source": str(id)})

text_cache = "ABCDEFGHIJ\nKLMNopqrstu\nvwyz.123"
last_key_id = None
cursor_index = 0
cursor_position = [0, 0]
KEYBOARD_PROGRAM_ID = 500

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

while True:
    keys = M.when_no_callback(KEYBOARD_PROGRAM_ID, "keys")
    if keys:
        if last_key_id is None:
            # Intial case. Catch up to lastest id but ignore cached text
            last_key_id = keys[-1]["id"]
            continue
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
                    elif d["special_key"] == "down":
                        cursor_position[1] = cursor_position[1] + 1
                    elif d["special_key"] == "right":
                        cursor_position[0] = cursor_position[0] + 1
                    elif d["special_key"] == "left":
                        if cursor_position[0] > 0:
                            cursor_position[0] = cursor_position[0] - 1
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

    time.sleep(0.01)

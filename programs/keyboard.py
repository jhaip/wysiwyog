from pynput import keyboard
import RPCClient
import json
import sys

M = RPCClient.RPCClient(use_http=True, rpc_url="http://10.0.0.223:5000")

id = sys.argv[1]

last_key_id = 0
cache = []
max_cache_size = 20

M.claim(id, "keys", cache)

def map_special_key(key):
    m = {}
    m[keyboard.Key.backspace] = "backspace"
    m[keyboard.Key.enter] = "enter"
    m[keyboard.Key.tab] = "tab"
    m[keyboard.Key.space] = "space"
    m[keyboard.Key.left] = "left"
    m[keyboard.Key.right] = "right"
    m[keyboard.Key.up] = "up"
    m[keyboard.Key.down] = "down"
    if key in m:
        return m[key]
    return None
    

def add_key(key, special_key):
    global last_key_id, cache, max_cache_size
    last_key_id += 1
    if special_key:
        special_key = map_special_key(special_key)
    cache.append({"id": last_key_id, "key": key, "special_key": special_key})
    if len(cache) > max_cache_size:
        cache.pop(0)
    M.claim(id, "keys", cache)

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
        add_key(key.char, None)
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
        add_key(None, key)

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

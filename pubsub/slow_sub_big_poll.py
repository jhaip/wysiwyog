import sys
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.SUB)
# socket.setsockopt(zmq.CONFLATE, 1)  # Only the latest receive msg in queue
# Doesn't work for multipart messages
socket.connect("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
if len(sys.argv) <= 1:
    print("must include filter args like 'A'")
    exit()

zip_filter = sys.argv[1]

# Python 2 - ascii bytes to unicode str
if isinstance(zip_filter, bytes):
    zip_filter = zip_filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)
socket.setsockopt_string(zmq.SUBSCRIBE, "C")

while True:
    lastVal = None
    lastC = None
    # Grab all messages as fast as we can, updating the cache along the way
    while True:
        try:
            string = socket.recv_string(flags=zmq.NOBLOCK)
            if string[0] == zip_filter:
                lastVal = string
            elif string[0] == "C":
                lastC = string
        except zmq.Again:
            break

    # Do the "slow processing"
    # In the background, messages may be accumulating in the zmq queue
    print("{}\t{}".format(lastVal, lastC))
    time.sleep(1)

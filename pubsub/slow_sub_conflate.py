import sys
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)  # Only the latest receive msg in queue
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
    string = socket.recv_string()
    print(string)
    time.sleep(1)

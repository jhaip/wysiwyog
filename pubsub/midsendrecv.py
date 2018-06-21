import sys
import zmq
import threading
import time
from random import randrange

if len(sys.argv) != 2:
    print("bad CLI argument")
    quit()

id = int(sys.argv[1])
sub_id = id
send_id = id + 1

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")
socket.setsockopt_string(zmq.SUBSCRIBE, str(sub_id))
socket_pub = context.socket(zmq.PUB)
socket_pub.connect("tcp://localhost:5555")

print("Collecting updates from {0}".format(sub_id))
print("procssing updates")

while True:
    # Block until a message comes in
    string = socket.recv_string()
    zipcode, temperature, relhumidity = string.split()
    print("received, now sending")
    # Then immediately send a message, then go back to waiting
    s = "%s %s %s" % (str(send_id), temperature, relhumidity)
    print("sending data", s)
    socket_pub.send_string(s)

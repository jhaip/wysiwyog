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

print("Collecting updates from {0}".format(sub_id))

def send_data(context, send_id):
    socket_pub = context.socket(zmq.PUB)
    socket_pub.connect("tcp://localhost:5555")

    while True:
        temperature = randrange(-80, 135)
        relhumidity = randrange(10, 60)
        s = "%s %i %i" % (str(send_id), temperature, relhumidity)
        print("sending data", s)
        socket_pub.send_string(s)
        time.sleep(1)

thread = threading.Thread(target=send_data, args=(context, send_id))
thread.start()

print("procssing updates")

# Process 5 updates
total_temp = 0
n_updates = 0
while n_updates < 5:
    # recv
    string = socket.recv_string()
    zipcode, temperature, relhumidity = string.split()
    total_temp += int(temperature)
    n_updates += 1
    print("received one", n_updates)

print("Average temperature for zipcode '%s' was %dF" % (
      str(sub_id), total_temp / (n_updates+1))
)

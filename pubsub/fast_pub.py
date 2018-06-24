import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://localhost:5555")

i = 0
while True:
    socket.send_string("A"+str(i))
    socket.send_string("B"+str(i))
    i += 1

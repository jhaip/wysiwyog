import zmq

context = zmq.Context(1)
frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:5555")
frontend.setsockopt(zmq.SUBSCRIBE, b"")
backend = context.socket(zmq.PUB)
backend.bind("tcp://*:5556")
zmq.device(zmq.FORWARDER, frontend, backend)

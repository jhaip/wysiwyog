import zmq
import logging
import json

logging.basicConfig(level=logging.INFO)


class RPCClient:

    def __init__(self):
        self.context = zmq.Context()
        logging.info("Connecting to hello world server…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")

    def _rpc(self, eventName, options):
        data = json.dumps({"event": eventName, "options": options})
        self.socket.send_string(data)
        message = self.socket.recv_string()
        return json.loads(message)

    def get_wishes_by_type(self, type):
        return self._rpc("get_wishes_by_type", type)

    def clear_wishes(self, opts):
        return self._rpc("clear_wishes", opts)

    def wish(self, type, source, action):
        return self._rpc("wish", {"type": type, "source": source, "action": action})

    def claim(self, source, key, value):
        return self._rpc("claim", {"source": source, "key": key, "value": value})

    def when(self, source, key, callback):
        val = self._rpc("when", {"source": source, "key": key})
        callback(val)

    def stop_program(self, id):
        return self._rpc("stop_program", {"id": id})

    def run_program(self, id, restart=False):
        return self._rpc("run_program", {"id": id, "restart": restart})

    def add_program(self, id, path, restart=False):
        return self._rpc("add_program", {"id": id, "path": path, "restart": restart})

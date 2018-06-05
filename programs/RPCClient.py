import zmq
import logging
import json

logging.basicConfig(level=logging.INFO)


class RPCClient:

    def __init__(self, use_http=False, rpc_url=None):
        if use_http:
            logging.info("Using HTTP RPC connection to server")
            self.RPC_URL = rpc_url
        else:
            self.context = zmq.Context()
            logging.info("Connecting to hello world server…")
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect("tcp://localhost:5555")
            self.image_socket = self.context.socket(zmq.REQ)
            self.image_socket.connect("tcp://localhost:5566")

    def _rpc(self, eventName, options):
        if use_http:
            r = None
            if eventName in ["get_wishes_by_type", "when", "get_image"]:
                r = requests.get(self.RPC_URL, params={"event": eventName, "options": options})
            else:
                r = requests.post(self.RPC_URL, json={"event": eventName, "options": options})
            r.raise_for_status()
            return r.json()
        else:
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

    def when_no_callback(self, source, key):
        return self._rpc("when", {"source": source, "key": key})

    def stop_program(self, id):
        return self._rpc("stop_program", {"id": id})

    def run_program(self, id, restart=False):
        return self._rpc("run_program", {"id": id, "restart": restart})

    def set_image(self, image_string):
        self.image_socket.send(image_string)
        message = self.image_socket.recv_string()
        return message

    def get_image(self):
        data = json.dumps({"event": "get_image", "options": {}})
        self.socket.send_string(data)
        message = self.socket.recv()
        return message

    def create_program(self, name):
        return self._rpc("create_program", {"name": name})

    def update_program(self, program_id, new_code):
        return self._rpc("update_program", {"program_id": program_id, "new_code": new_code})

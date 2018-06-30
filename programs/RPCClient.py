import zmq
import logging
import json
import requests
import IlluminationHelper
import PointingAtHelper

logging.basicConfig(level=logging.INFO)

context = zmq.Context()

class RPCClient:

    def __init__(self, rpc_url='localhost'):
        self.sub_socket = context.socket(zmq.SUB)
        self.sub_socket.connect("tcp://{0}:5556".format(rpc_url))
        self.pub_socket = context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://{0}:5555".format(rpc_url))

    def set_pub_high_water_mark(self, n):
        self.pub_socket.set_hwm(n)

    # def _rpc(self, eventName, options):
    #     if self.use_http:
    #         r = None
    #         if eventName in ["get_wishes_by_type", "when", "get_image"]:
    #             logging.info("Making a GET Request")
    #             r = requests.get(self.RPC_URL, params={"event": eventName, "options": json.dumps(options)})
    #         else:
    #             logging.info("Making a POST Request")
    #             r = requests.post(self.RPC_URL, json={"event": eventName, "options": options})
    #         r.raise_for_status()
    #         return r.json()
    #     else:
    #         data = json.dumps({"event": eventName, "options": options})
    #         self.socket.send_string(data)
    #         message = self.socket.recv_string()
    #         return json.loads(message)

    def get_wishes_by_type(self, type):
        sub_string = "WISH[{0}/".format(type)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_string)
        string = self.sub_socket.recv_string()
        val = string[len(sub_string):]
        json_val = json.loads(val)
        return json_val

    def clear_wishes(self, opts):
        # return self._rpc("clear_wishes", opts)
        # TODO
        return None

    def wish(self, type, source, action):
        s = "WISH[{0}/{1}]{2}".format(type, source, action)
        self.pub_socket.send_string(s)

    def claim(self, source, key, value):
        json_value = json.dumps(value)
        s = "CLAIM[{0}/{1}]{2}".format(source, key, json_value)
        # logging.error(s)
        self.pub_socket.send_string(s, zmq.NOBLOCK)

    def fastclaim(self, source, key, value):
        # TODO: remove
        return None

    def when(self, source, key, callback):
        json_val = self.when_no_callback(source, key)
        callback(json_val)

    def when_set_filter(self, filter_str):
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, filter_str)

    def when_clear_filter(self, filter_str):
        self.sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, filter_str)

    def when_recv(self):
        return self.sub_socket.recv_string()

    def when_multiple(self, whens):
        for when in whens:
            sub_string = "CLAIM[{0}/{1}]".format(when["source"], when["key"])
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_string)
        string = self.sub_socket.recv_string()
        val = string[len(sub_string):]
        json_val = json.loads(val)
        return json_val

    def when_no_callback(self, source, key):
        sub_string = "CLAIM[{0}/{1}]".format(source, key)
        logging.error("looking for: " + sub_string)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_string)
        # TODO: don't do this ^ every time
        string = self.sub_socket.recv_string()
        logging.error("got string! : " + string)
        val = string[len(sub_string):]
        json_val = val
        try:
            json_val = json.loads(val)
        except:
            pass
        logging.error("returning for " + sub_string)
        return json_val

    def stop_program(self, id):
        data = json.dumps({"id": id, "action": "stop"})
        return self.wish("PROGRAM", "idk", data)

    def run_program(self, id, restart=False):
        data = json.dumps({"id": id, "restart": restart, "action": "run"})
        return self.wish("PROGRAM", "idk", data)

    def set_image(self, image_string):
        # self.image_socket.send(image_string)
        # message = self.image_socket.recv_string()
        # return message
        return None

    def get_image(self):
        # data = json.dumps({"event": "get_image", "options": {}})
        # self.socket.send_string(data)
        # message = self.socket.recv()
        # return message
        return None

    def create_program(self, name):
        data = json.dumps({"action": "create", "name": name})
        return self.wish("PROGRAM", "idk", data)

    def update_program(self, program_id, new_code):
        data = json.dumps({"action": "update", "id": program_id, "new_code": new_code})
        return self.wish("PROGRAM", "idk", data)

    def new_illumination(self, target):
        return IlluminationHelper.Illumination(target)

    def get_paper_you_point_at(self, papers, id, WISKER_LENGTH):
        return PointingAtHelper.get_paper_you_point_at(papers, id, WISKER_LENGTH)

    def draw_wisker(self, papers, id, WISKER_LENGTH):
        me = PointingAtHelper.get_my_paper(papers, id)
        ill = self.new_illumination("global")
        if me is not None:
            wisker = PointingAtHelper.get_paper_wisker(me, "up", WISKER_LENGTH)
            ill.stroke(0, 255, 0)
            ill.line(wisker[0]["x"], wisker[0]["y"], wisker[1]["x"], wisker[1]["y"])
        self.wish("DRAW", id, ill.package())

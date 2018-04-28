import zmq
import logging
import json
import psutil
import uuid

logging.basicConfig(level=logging.INFO)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


class Master:

    def __init__(self):
        self.wishes = []
        self.state = {}
        self.programs = {}

    def clear_wishes(self, opts):
        def keep(w):
            return any(map(lambda k: w.get(k) != opts[k], opts.keys()))
        self.wishes = list(filter(keep, self.wishes))
        logging.info("WISH CLEARED")
        logging.info(self.wishes)

    def get_wishes_by_type(self, type):
        return list(filter(lambda w: w.get("type") == type, self.wishes))

    def wish(self, type, source, action):
        self.clear_wishes({"type": type, "source": source})
        self.wishes.append({
            "id": str(uuid.uuid4()),
            "type": type,
            "source": source,
            "action": action
        })
        logging.info("WISH ADDED")
        logging.info(self.wishes)

    def claim(self, source, key, value):
        if source not in self.state:
            self.state[source] = {}
        self.state[source][key] = value
        logging.info("CLAIM ADDED")
        logging.info(self.state)

    def when(self, source, key):
        return self.state.get(source, {}).get(key)

    def stop_program(self, id):
        if id in self.programs:
            pid = self.programs[id].get("pid")
            if pid is not None and psutil.pid_exists(pid):
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=1)  # This might be blocking?
                self.programs[id]["pid"] = None
                logging.info("PROGRAM STOPPED")
                logging.info(self.programs)
        else:
            logging.error("Program with id %s does not exist" % id)

    def run_program(self, id, restart=False):
        if id in self.programs:
            pid = self.programs[id].get("pid")
            if pid is not None and psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if restart or p.status() == psutil.STATUS_ZOMBIE:
                    p.terminate()
                    p.wait(timeout=1)  # This might be blocking?
                else:
                    return  # let it keep running
            p = psutil.Popen(["python", self.programs[id]["path"]])
            self.programs[id]["pid"] = p.pid
            logging.info("PROGRAM STARTED")
            logging.info(self.programs)
        else:
            logging.error("Program with id %s does not exist" % id)

    def add_program(self, id, path_to_code, restart=False):
        self.programs[id] = {"path": path_to_code}
        logging.info("PROGRAM ADDED")
        logging.info(self.programs)
        if restart:
            self.run_program(id, True)


master = Master()

while True:
    message = socket.recv_string()
    logging.info("Received request: %s" % message)
    message_json = json.loads(message)
    event = message_json["event"]
    options = message_json["options"]
    noop = json.dumps({})
    if event == "clear_wishes":
        master.clear_wishes(options)
        socket.send_string(noop)
    elif event == "get_wishes_by_type":
        val = master.get_wishes_by_type(options)
        data = json.dumps(val)
        socket.send_string(data)
    elif event == "wish":
        master.wish(options["type"], options["source"], options["action"])
        socket.send_string(noop)
    elif event == "claim":
        master.claim(options["source"], options["key"], options["value"])
        socket.send_string(noop)
    elif event == "when":
        val = master.when(options["source"], options["key"])
        data = json.dumps(val)
        socket.send_string(data)
    elif event == "stop_program":
        master.stop_program(options["id"])
        socket.send_string(noop)
    elif event == "run_program":
        master.run_program(options["id"], options.get("restart", False))
        socket.send_string(noop)
    elif event == "add_program":
        master.add_program(options["id"], options["path"], options.get("restart", False))
        socket.send_string(noop)

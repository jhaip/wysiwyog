import time
import zmq
import logging
import json
import psutil
import uuid
import sqlite3
import random
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

context = zmq.Context()
string_socket = context.socket(zmq.REP)
string_socket.bind("tcp://*:5555")

image_socket = context.socket(zmq.REP)
image_socket.bind("tcp://*:5566")

conn = sqlite3.connect('code.db')


class Master:

    def __init__(self):
        self.wishes = []
        self.state = {}
        self.programs = {}
        self.image = None
        self._init_db()
        self._init_program_state()

    def _init_db(self):
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS programs (id TEXT PRIMARY KEY, name TEXT, filename TEXT)")
        conn.commit()

        n_programs = c.execute("SELECT COUNT(*) FROM programs").fetchone()[0]
        if n_programs == 0:
            self.create_program("boot", "programs/boot.py", 0)
            self.create_program("one_tick", "programs/one_tick.py", 1)
            self.create_program("clock", "programs/clock.py", 2)
            self.create_program("drawer1", "programs/drawer1.py", 1072)
            self.create_program("fox_claimer", "programs/fox_claimer.py", 1054)
            self.create_program("fox_conditional", "programs/fox_conditional.py", 1688)
            self.create_program("projector", "programs/projector.py", 6)
            self.create_program("run_papers", "programs/run_papers.py", 7)
            self.create_program("code_mgmt_test", "programs/code_mgmt_test.py", 99)

    def _init_program_state(self):
        c = conn.cursor()
        for row in c.execute("SELECT id, filename FROM programs"):
            self.programs[row[0]] = {"path": row[1]}

    def clear_wishes(self, opts):
        def keep(w):
            return any(map(lambda k: str(w.get(k)) != str(opts[k]), opts.keys()))
        self.wishes = list(filter(keep, self.wishes))
        logging.info("WISH CLEARED")
        logging.info(self.wishes)

    def get_wishes_by_type(self, type):
        return list(filter(lambda w: str(w.get("type")) == str(type), self.wishes))

    def wish(self, type, source, action):
        type = str(type)
        source = str(source)
        self.clear_wishes({"type": type, "source": source})
        self.wishes.append({
            "id": str(uuid.uuid4()),
            "type": str(type),
            "source": str(source),
            "action": str(action)
        })
        logging.info("WISH ADDED")
        logging.info(self.wishes)

    def claim(self, source, key, value):
        source = str(source)
        key = str(key)
        if source not in self.state:
            self.state[source] = {}
        self.state[source][key] = value
        logging.info("CLAIM ADDED")
        logging.info(self.state)

    def clear_claims(self, source):
        source = str(source)
        self.state[source] = {}
        logging.info("CLEAR CLAIMS")
        logging.info(self.state)

    def when(self, source, key):
        source = str(source)
        key = str(key)
        if source == "code":
            return self._get_program_description(key)
        return self.state.get(source, {}).get(key)

    def _generate_program_id(self):
        max_number = 8400 // 4
        existing_ids = []
        potential_ids = []
        c = conn.cursor()
        for row in c.execute("SELECT id FROM programs"):
            logging.error(row)
            existing_ids.append(row[0])
        for i in range(max_number):
            if i not in existing_ids:
                potential_ids.append(i)
        if len(potential_ids) is 0:
            raise Exception("No more program IDs available. Max number of programs reaached")
        return random.choice(potential_ids)

    def create_program(self, name, existing_filename=None, force_id=None):
        logging.error("CREATE NEW PROGRAM")
        logging.error(name)
        logging.error(existing_filename)
        # Create a program with the given name, empty code, and a chosen ID
        new_id = force_id
        if force_id is None:
            new_id = self._generate_program_id()
        new_id = str(new_id)
        filename = existing_filename
        if existing_filename is None:
            filename = "programs/" + name + ".py"
            with open(filename, 'w') as f:
                f.write("")
        new_program = (new_id, name, filename)
        c = conn.cursor()
        c.execute("INSERT INTO programs VALUES (?,?,?)", new_program)
        conn.commit()
        self.programs[new_id] = {"path": filename}
        logging.error(type(new_id))
        logging.error(self.programs)
        return new_id

    def update_program(self, program_id, new_code):
        logging.error("UPDATE PROGRAM")
        logging.error(program_id)
        logging.error(new_code)
        c = conn.cursor()
        path = None
        for row in c.execute("SELECT filename FROM programs WHERE id = ?", (str(program_id),)):
            logging.error(row)
            path = row[0]
        if path is None:
            return None
        with open(path, 'w') as f:
            f.write(new_code)
        self.stop_program(program_id)
        return True

    def _get_program_description(self, program_id):
        c = conn.cursor()
        path = None
        name = None
        for row in c.execute("SELECT filename, name FROM programs WHERE id = ?", (str(program_id),)):
            logging.error(row)
            path = row[0]
            name = row[1]
        if path is None:
            return None
        p = Path(path)
        text = p.read_text()
        logging.error("_GET SOURCE CODE:")
        logging.error(text)
        return {"code": text, "name": name}

    def stop_program(self, id):
        id = str(id)
        if id in self.programs:
            pid = self.programs[id].get("pid")
            if pid is not None and psutil.pid_exists(pid):
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=1)  # This might be blocking?
                self.programs[id]["pid"] = None
            self.clear_wishes({"source": str(id)})
            self.clear_claims(str(id))
        else:
            logging.error("Program with id %s does not exist" % id)

    def run_program(self, id, restart=False):
        id = str(id)
        if id in self.programs:
            pid = self.programs[id].get("pid")
            if pid is not None and psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if restart or p.status() == psutil.STATUS_ZOMBIE:
                    p.terminate()
                    p.wait(timeout=1)  # This might be blocking?
                    if restart:
                        self.clear_wishes({"source": str(id)})
                        self.clear_claims(str(id))
                else:
                    return  # let it keep running
            p = psutil.Popen(["python", self.programs[id]["path"], str(id)])
            self.programs[id]["pid"] = p.pid
            logging.info("PROGRAM STARTED")
            logging.info(self.programs)
        else:
            logging.error("Program with id %s does not exist" % id)

    def set_image(self, image_string):
        self.image = image_string
        logging.info("IMAGE SET")

    def get_image(self):
        return self.image


master = Master()
master.run_program(99)

def process_string_socket():
    while True:
        try:
            message = string_socket.recv_string(zmq.DONTWAIT)
        except zmq.Again:
            return
        # process task
        logging.info("Received request: %s" % message)
        message_json = json.loads(message)
        event = message_json["event"]
        options = message_json["options"]
        noop = json.dumps({})
        if event == "clear_wishes":
            master.clear_wishes(options)
            string_socket.send_string(noop)
        elif event == "get_wishes_by_type":
            val = master.get_wishes_by_type(options)
            data = json.dumps(val)
            string_socket.send_string(data)
        elif event == "wish":
            master.wish(options["type"], options["source"], options["action"])
            string_socket.send_string(noop)
        elif event == "claim":
            master.claim(options["source"], options["key"], options["value"])
            string_socket.send_string(noop)
        elif event == "when":
            val = master.when(options["source"], options["key"])
            data = json.dumps(val)
            string_socket.send_string(data)
        elif event == "stop_program":
            master.stop_program(options["id"])
            string_socket.send_string(noop)
        elif event == "run_program":
            master.run_program(options["id"], options.get("restart", False))
            string_socket.send_string(noop)
        elif event == "get_image":
            string_socket.send(master.get_image())
        elif event == "create_program":
            logging.error("************")
            new_id = master.create_program(options["name"])
            data = json.dumps({"id": new_id})
            logging.error("returning data")
            logging.error(new_id)
            logging.error(data)
            string_socket.send_string(data)
        elif event == "update_program":
            master.update_program(options["program_id"], options["new_code"])
            string_socket.send_string(noop)


def process_image_socket():
    while True:
        try:
            message = image_socket.recv(zmq.DONTWAIT)
        except zmq.Again:
            return
        # process task
        logging.info("Received image")
        master.set_image(message)
        noop = json.dumps({})
        image_socket.send_string(noop)


while True:
    process_string_socket()
    process_image_socket()
    time.sleep(0.001)

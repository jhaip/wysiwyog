import time
import zmq
import logging
import json
import psutil
import uuid
import sqlite3
import random
from pathlib import Path

logging.basicConfig(level=logging.INFO)

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://{0}:5556".format(rpc_url))
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://{0}:5555".format(rpc_url))

conn = sqlite3.connect('code.db')

class Master:

    def __init__(self):
        self.programs = {}
        self.boot_programs = ['0', '7', '8', '99']
        self._init_db()
        self._init_program_state()

    def _init_db(self):
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS programs (id TEXT PRIMARY KEY, name TEXT, filename TEXT)")
        conn.commit()

        n_programs = c.execute("SELECT COUNT(*) FROM programs").fetchone()[0]
        if n_programs == 0:
            logging.error("SEEDING DATABASE")
            self.create_program("boot", "programs/boot.py", 0)
            self.create_program("one_tick", "programs/one_tick.py", 1)
            self.create_program("clock", "programs/clock.py", 2)
            self.create_program("drawer1", "programs/drawer1.py", 1072)
            self.create_program("fox_claimer", "programs/fox_claimer.py", 1054)
            self.create_program("fox_conditional", "programs/fox_conditional.py", 1688)
            self.create_program("run_papers", "programs/run_papers.py", 7)
            self.create_program("http_rpc", "programs/http_rpc.py", 8)
            self.create_program("gui_projector", "programs/gui_projector.py", 9)
            self.create_program("frame-to-dots", "programs/frame-to-dots.py", 10)
            self.create_program("code_mgmt_test", "programs/code_mgmt_test.py", 99)
            self.create_program("taco", "programs/taco--670.py", 670)
            self.create_program("draw_angle", "programs/draw_angle--1790.py", 1790)
            self.create_program("paper_dot_counter", "programs/paper_dot_counter--1691.py", 1691)

    def _init_program_state(self):
        c = conn.cursor()
        for row in c.execute("SELECT id, filename FROM programs"):
            self.programs[row[0]] = {"path": row[1]}

    def _list_non_boot_papers(self):
        papers = list(self.programs.keys())
        return list(filter(lambda x: x not in self.boot_programs, papers))

    def clear_wishes(self, opts):
        # TODO: publish clear signal or tombstone
        pass

    def clear_claims(self, source):
        source = str(source)
        # TODO: publish clear signal or tombstone
        return

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
            filename = "programs/" + name + "--" + str(new_id) + ".py"
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
            try:
                p = psutil.Popen(["python", self.programs[id]["path"], str(id)])
                self.programs[id]["pid"] = p.pid
            except:
                logging.error("Error starting program", str(id))
                logging.error("Unexpected error:", sys.exc_info()[0])
        else:
            logging.error("Program with id %s does not exist" % id)


master = Master()
master.run_program(0)

sub_socket.setsockopt_string(zmq.SUBSCRIBE, "WISH[PROGRAM/")

while True:
    string = sub_socket.recv_string()
    val = string.split(']', 1)[1]
    json_val = json.loads(val)
    logging.info(json_val)
    action = json_val["action"]
    if action == "stop":
        id = json_val["id"]
        master.stop_program(id)
    elif action == "run":
        id = json_val["id"]
        restart = json_val["restart"]
        master.run_program(id, restart)
    elif action == "create":
        name = json_val["name"]
        master.create_program(name)
    elif action == "update":
        id = json_val["id"]
        new_code = json_val["new_code"]
        master.create_program(id, new_code)

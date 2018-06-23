import logging
import sys
import time
import zmq

logging.basicConfig(level=logging.INFO)

id = sys.argv[1]

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://{0}:5555".format(rpc_url))
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://{0}:5556".format(rpc_url))
sub_string = "CLAIM[global/papers]"
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_string)

boot_programs = ['0', '7', '8', '99']

while True:
    string = sub_socket.recv_string()
    val = string(len(sub_string):)
    papers = json.loads(val)
    if papers:
        logging.debug("-- got papers %s" % len(papers))
        for paper in papers:
            paper_id = int(paper["id"])
            if paper["id"] in non_boot_papers:
                logging.debug("running %s" % paper_id)
                M.run_program(paper_id)
                non_boot_papers.remove(paper["id"])
        # Stop papers that aren't present
        for id in non_boot_papers:
            logging.debug("STOP %s" % id)
            M.stop_program(id)

        M.when("global", "papers", receivePapers)

    M.when("list_papers", "-", receive_list)

    time.sleep(0.01)

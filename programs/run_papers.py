import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

while True:

    def receive_list(non_boot_papers):

        def receivePapers(papers):
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

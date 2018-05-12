import logging
import sys
import time
import RPCClient

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

while True:

    def receivePapers(papers):
        papers_to_run = [1072, 1054, 1688]
        if papers:
            logging.info("-- got papers %s" % len(papers))
            for paper in papers:
                paper_id = int(paper["id"])
                if paper_id in papers_to_run:
                    logging.info("running %s" % paper_id)
                    M.run_program(paper_id)
                    papers_to_run.remove(paper_id)
            # Stop papers that aren't present
            for id in papers_to_run:
                logging.info("STOP %s" % id)
                M.stop_program(id)
    M.when("global", "papers", receivePapers)

    time.sleep(0.01)

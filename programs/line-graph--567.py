import logging
import sys
import RPCClient
import json
import time

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()
id = sys.argv[1]
time.sleep(1)
M.when_set_filter("CLAIM[global/papers]")
paper_im_pointing_at = None
paper_claim_str = None
WISKER_LENGTH = 150
cache = []

while True:
    string = M.when_recv()
    msg_prefix = string.split(']', 1)[0] + "]"
    val = json.loads(string[len(msg_prefix):])
    if "papers" in msg_prefix:
        papers = val
        prev_paper = None
        paper_im_pointing_at = M.get_paper_you_point_at(papers, id, WISKER_LENGTH)
        M.draw_wisker(papers, id, WISKER_LENGTH)
        if paper_im_pointing_at is not None and prev_paper != paper_im_pointing_at:
            if paper_claim_str:
                M.when_clear_filter(paper_claim_str)
            paper_claim_str = "CLAIM[" + str(paper_im_pointing_at)
            M.when_set_filter(paper_claim_str)
    elif "CLAIM" in msg_prefix:
        logging.error("-------------------------------")
        logging.error(val)
        if len(val.get("list", [])) > 0:
            ill = M.new_illumination(id)
            ill.text("LINE GRAPH:", 10, 10)
            ill.stroke(255, 255, 0)
            ill.strokewidth(5)
            try:
                width = 100.
                height = 100.
                step = width / len(val["list"])
                number_list = list(map(float, val["list"]))
                max_number = max(number_list) * 1.0
                for i, v in enumerate(number_list):
                    if i > 0:
                        ill.line((i-1)*step, height * number_list[i-1] / max_number, i*step, height * number_list[i] / max_number)
            except:
                logging.error(sys.exc_info()[0])
            M.wish("DRAW", id, ill.package())
        else:
            ill = M.new_illumination(id)
            ill.text("that paper has no number list", 10, 10)
            M.wish("DRAW", id, ill.package())

    if paper_im_pointing_at is None:
        ill = M.new_illumination(id)
        ill.text("no data yet", 10, 10)
        M.wish("DRAW", id, ill.package())

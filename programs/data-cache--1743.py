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
        if True:
            try:
                vi = float(val)
                cache.insert(0, vi)
                if len(cache) > 10:
                    cache.pop()
                M.claim(str(id), "data", {"list": cache})
                # time.sleep(0.5)
            except ValueError:
                logging.error("VALUE error :(")
                pass

    ill = M.new_illumination(id)
    cache_str = list(map(str, cache))
    ill.text("\n".join(cache_str), 10, 10)
    ill.fontcolor(0,200,255)
    ill.text(str(paper_im_pointing_at), 10, 10)
    ill.text(str(paper_claim_str), 10, 25)
    M.wish("DRAW", id, ill.package())
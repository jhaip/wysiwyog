import logging
import sys
import RPCClient
import time
import json

M = RPCClient.RPCClient()
id = sys.argv[1]

time.sleep(1)
M.when_set_filter("CLAIM[global/papers]")
M.when_set_filter("CLAIM[500/keys]")
paper_im_pointing_at = None
paper_last_key_id = None
WISKER_LENGTH = 150

while True:
    string = M.when_recv()
    msg_prefix = string.split("]", 1)[0]
    msg = string.split("]", 1)[1]
    val = json.loads(msg)
    if "papers" in msg_prefix:
        papers = val
        prev_pointing_at = paper_im_pointing_at
        paper_im_pointing_at = M.get_paper_you_point_at(papers, id, WISKER_LENGTH)
        if paper_im_pointing_at != prev_pointing_at:
            paper_last_key_id = None
        M.draw_wisker(papers, id, WISKER_LENGTH)

        ill = M.new_illumination(id)
        if paper_im_pointing_at is not None:
            ill.text(paper_im_pointing_at, 10, 10)
        else:
            ill.text("None", 10, 10)
        M.wish("DRAW", id, ill.package())
    elif "keys" in msg_prefix:
        keys = val
        if paper_im_pointing_at is not None and keys:
            if paper_last_key_id is None:
                paper_last_key_id = keys[-1]["id"] - 1
            papers_keys = list(filter(lambda p: p["id"] > paper_last_key_id, keys))
            if papers_keys:
                paper_last_key_id = papers_keys[-1]["id"]
                M.claim(paper_im_pointing_at, "keys", papers_keys)

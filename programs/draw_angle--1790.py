import logging
import sys
import RPCClient
import time
import math

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

def dist(p1, p2):
    return math.sqrt( (p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2 )

def receivePapers(papers):
    if papers:
        for paper in papers:
            if paper["id"] == str(id) and len(paper["corners"]) == 4:
                tl = None
                tr = None
                bl = None
                for corner in paper["corners"]:
                    if corner["CornerId"] == 0:
                        tl = corner
                    elif corner["CornerId"] == 1:
                        tr = corner
                    elif corner["CornerId"] == 3:
                        bl = corner
                paper_width = dist(tl, tr)
                paper_height = dist(tl, bl)
                paper_origin = tl
                paper_angle = math.atan2(tr["y"] - tl["y"], tr["x"] - tl["x"])

                ill = M.new_illumination(id)
                # ill.fontsize(16)
                text = "R: {0:.3f}\nW: {1:.0f}\nH: {2:.0f}".format(paper_angle, paper_width, paper_height)
                ill.text(text, 20, 20)
                M.wish("DRAW", id, ill.package())

while True:
    M.when("global", "papers", receivePapers)
    time.sleep(0.5)

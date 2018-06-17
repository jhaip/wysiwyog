import logging
import sys
import RPCClient
import time
import math

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

def on_segment(p, q, r):
    '''Given three colinear points p, q, r, the function checks if
    point q lies on line segment "pr"
    '''
    if (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
        q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])):
        return True
    return False

def orientation(p, q, r):
    '''Find orientation of ordered triplet (p, q, r).
    The function returns following values
    0 --> p, q and r are colinear
    1 --> Clockwise
    2 --> Counterclockwise
    '''

    val = ((q[1] - p[1]) * (r[0] - q[0]) -
            (q[0] - p[0]) * (r[1] - q[1]))
    if val == 0:
        return 0  # colinear
    elif val > 0:
        return 1   # clockwise
    else:
        return 2  # counter-clockwise

def do_intersect(p1, q1, p2, q2):
    '''Main function to check whether the closed line segments p1 - q1 and p2
       - q2 intersect'''
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2 and o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0 and on_segment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are colinear and q2 lies on segment p1q1
    if (o2 == 0 and on_segment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0 and on_segment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0 and on_segment(p2, q1, q2)):
        return True

    return False # Doesn't fall in any of the above cases

def is_dot_in_paper(tl, tr, br, bl, dot):
    center_x = (tl["x"] + tr["x"] + br["x"] + bl["x"]) / 4.0
    center_y = (tl["y"] + tr["y"] + br["y"] + bl["y"]) / 4.0
    # Make it 10% smaller to avoid counting dots on the actual corners
    conv = lambda x: ((x["x"] - center_x) * 0.9, (x["y"] - center_y) * 0.9)
    tl_ = conv(tl)
    tr_ = conv(tr)
    br_ = conv(br)
    bl_ = conv(bl)
    dot_ = (dot["x"] - center_x, dot["y"] - center_y)
    dotray_ = (dot_[0] + 1000000, dot_[1])
    n_crosses = 0

    if do_intersect(tl_, tr_, dot_, dotray_):
        n_crosses += 1
    if do_intersect(tr_, br_, dot_, dotray_):
        n_crosses += 1
    if do_intersect(br_, bl_, dot_, dotray_):
        n_crosses += 1
    if do_intersect(bl_, tl_, dot_, dotray_):
        n_crosses += 1

    # TODO: handle special case of crossing the mid point exactly

    return n_crosses >= 1 and n_crosses % 2 == 1

def receiveDots(papers, dots):
    if dots:
        counter(papers, dots)

def receivePapers(papers):
    if papers:
        M.when("global", "dots", lambda d: receiveDots(papers, d))

def counter(papers, dots):
    for paper in papers:
        if paper["id"] == str(id) and len(paper["corners"]) == 4:
            tl = None
            tr = None
            bl = None
            br = None
            for corner in paper["corners"]:
                if corner["CornerId"] == 0:
                    tl = corner
                elif corner["CornerId"] == 1:
                    tr = corner
                elif corner["CornerId"] == 2:
                    br = corner
                elif corner["CornerId"] == 3:
                    bl = corner

            n_dots = 0

            for dot in dots:
                if is_dot_in_paper(tl, tr, br, bl, dot):
                    n_dots += 1

            ill = M.new_illumination(id)
            ill.fontsize(16)
            text = "{0} dots".format(n_dots)
            ill.text(text, 20, 20)
            M.wish("DRAW", id, ill.package())

while True:
    M.when("global", "papers", receivePapers)
    time.sleep(1)

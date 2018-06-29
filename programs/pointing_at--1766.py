import logging
import sys
import RPCClient
import json
import time
import math

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

def get_papers_corners(paper):
    tl = None
    tr = None
    br = None
    bl = None
    for corner in paper["corners"]:
        if corner["CornerId"] == 0:
            tl = corner
        elif corner["CornerId"] == 1:
            tr = corner
        elif corner["CornerId"] == 2:
            br = corner
        elif corner["CornerId"] == 3:
            bl = corner
    return (tl, tr, br, bl)

def get_paper_center(c):
    logging.error(c)
    x = (c[0]["x"] + c[1]["x"] + c[2]["x"] + c[3]["x"]) * 0.25
    y = (c[0]["y"] + c[1]["y"] + c[2]["y"] + c[3]["y"]) * 0.25
    return {"x": x, "y": y}

def move_along_vector(amount, vector):
    size = math.sqrt(vector["x"]**2 + vector["y"]**2)
    C = 1.0 * amount / size
    return {"x": C * vector["x"], "y": C * vector["y"]}

def add_vec(vec1, vec2):
    return {"x": vec1["x"] + vec2["x"], "y": vec1["y"] + vec2["y"]}

def diff_vec(vec1, vec2):
    return {"x": vec1["x"] - vec2["x"], "y": vec1["y"] - vec2["y"]}

def scale_vec(vec, scale):
    return {"x": vec["x"] * scale, "y": vec["y"] * scale}

def get_paper_wisker(corners, direction, length):
    center = get_paper_center(corners)
    segment = None
    if direction == 'right':
        segment = (corners[1], corners[2])
    elif direction == 'down':
        segment = (corners[2], corners[3])
    elif direction == 'left':
        segment = (corners[3], corners[0])
    else:
        segment = (corners[0], corners[1])
    segmentMiddle = add_vec(segment[1], scale_vec(diff_vec(segment[0], segment[1]), 0.5))
    wiskerEnd = add_vec(segmentMiddle, move_along_vector(length, diff_vec(segmentMiddle, center)))
    return (segmentMiddle, wiskerEnd)

# Adapted from https://stackoverflow.com/questions/9043805/test-if-two-lines-intersect-javascript-function
def intersects(v1,  v2,  v3,  v4):
    det = (v2["x"] - v1["x"]) * (v4["y"] - v3["y"]) - (v4["x"] - v3["x"]) * (v2["y"] - v1["y"])
    if det == 0:
        return False
    else:
        _lambda = ((v4["y"] - v3["y"]) * (v4["x"] - v1["x"]) + (v3["x"] - v4["x"]) * (v4["y"] - v1["y"])) / det
        gamma = ((v1["y"] - v2["y"]) * (v4["x"] - v1["x"]) + (v2["x"] - v1["x"]) * (v4["y"] - v1["y"])) / det
        return (0 < _lambda and _lambda < 1) and (0 < gamma and gamma < 1)

def get_my_paper(papers, you_id):
    for paper in papers:
        if len(paper["corners"]) == 4:
            tl, tr, br, bl = get_papers_corners(paper)
            if paper["id"] == str(you_id):
                return (tl, tr, br, bl)
    return None

def get_paper_you_point_at(papers, you_id, WISKER_LENGTH):
    valid_papers = []
    my_paper = None
    for paper in papers:
        if len(paper["corners"]) == 4:
            tl, tr, br, bl = get_papers_corners(paper)
            if paper["id"] == str(you_id):
                my_paper = (tl, tr, br, bl)
            else:
                paper["ordered_corners"] = (tl, tr, br, bl)
                valid_papers.append(paper)
    if my_paper is not None and len(valid_papers) > 0:
        wisker = get_paper_wisker(my_paper, "up", WISKER_LENGTH)
        for paper in valid_papers:
            corners = paper["ordered_corners"]
            if intersects(wisker[0], wisker[1], corners[0], corners[1]) or \
               intersects(wisker[0], wisker[1], corners[1], corners[2]) or \
               intersects(wisker[0], wisker[1], corners[2], corners[3]) or \
               intersects(wisker[0], wisker[1], corners[3], corners[0]):
                return paper["id"]
    return None

time.sleep(1)  # Allow subscribers to connect
M.when_set_filter("CLAIM[global/papers]")
paper_im_pointing_at = None
WISKER_LENGTH = 150

while True:
    string = M.when_recv()
    event_type = string.split('[', 1)[0]  # WISH, CLAIM
    msg_prefix = string.split(']', 1)[0] + "]"
    val = json.loads(string[len(msg_prefix):])
    if "papers" in msg_prefix:
        papers = val
        point_im_pointing_at = get_paper_you_point_at(papers, id, WISKER_LENGTH)

        # Draw a label of what I'm pointing at
        ill = M.new_illumination(id)
        ill.fontsize(40)
        ill.fontcolor(100, 255, 255)
        if point_im_pointing_at is not None:
            ill.text(str(point_im_pointing_at), 10, 10)
        else:
            ill.text("None", 10, 10)
        M.wish("DRAW", id, ill.package())

        # Draw wisker:
        me = get_my_paper(papers, id)
        ill = M.new_illumination("global")
        if me is not None:
            wisker = get_paper_wisker(me, "up", WISKER_LENGTH)
            ill.stroke(0, 255, 0)
            ill.line(wisker[0]["x"], wisker[0]["y"], wisker[1]["x"], wisker[1]["y"])
        M.wish("DRAW", id, ill.package())

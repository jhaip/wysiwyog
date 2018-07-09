import logging
import json

logging.basicConfig(level=logging.INFO)


class Illumination:

    def __init__(self, target):
        self.target = target
        self.illuminations = []

    def rectangle(self, x, y, w, h):
        self.illuminations.append({
            "type": "rectangle",
            "options": { "x": x, "y": y, "w": w, "h": h }
        })

    def ellipse(self, x, y, w, h):
        self.illuminations.append({
            "type": "ellipse",
            "options": { "x": x, "y": y, "w": w, "h": h }
        })

    def text(self, text, x, y):
        self.illuminations.append({
            "type": "text",
            "options": { "x": x, "y": y, "text": text }
        })

    def line(self, x1, y1, x2, y2):
        self.illuminations.append({
            "type": "line",
            "options": [x1, y1, x2, y2]
        })

    def polygon(self, points):
        self.illuminations.append({
            "type": "polygon",
            "options": points
        })

    def fill(self, r, g=None, b=None, a=None):
        data = {}
        if type(r) is str:
            data = r  # color name like "blue"
        elif a is None:
            data = [r, g, b]
        else:
            data = [r, g, b, a]
        self.illuminations.append({
            "type": "fill",
            "options": data
        })

    def stroke(self, r, g=None, b=None, a=None):
        data = {}
        if type(r) is str:
            data = r  # color name like "blue"
        elif a is None:
            data = [r, g, b]
        else:
            data = [r, g, b, a]
        self.illuminations.append({
            "type": "stroke",
            "options": data
        })

    def nostroke(self):
        self.illuminations.append({ "type": "nostroke" })

    def nofill(self):
        self.illuminations.append({ "type": "nofill" })

    def strokewidth(self, width):
        self.illuminations.append({
            "type": "strokewidth",
            "options": width
        })

    def fontsize(self, size):
        self.illuminations.append({
            "type": "fontsize",
            "options": size
        })

    def fontcolor(self, r, g, b):
        self.illuminations.append({
            "type": "fontcolor",
            "options": [r, g, b]
        })

    def push(self):
        self.illuminations.append({ "type": "push" })

    def pop(self):
        self.illuminations.append({ "type": "pop" })

    def translate(self, x, y):
        self.illuminations.append({
            "type": "translate",
            "options": { "x": x, "y": y }
        })

    def rotate(self, angle):
        self.illuminations.append({
            "type": "rotate",
            "options": angle
        })

    def scale(self, x, y):
        self.illuminations.append({
            "type": "scale",
            "options": { "x": x, "y": y }
        })

    def package(self):
        d = {}
        d[str(self.target)] = self.illuminations
        return json.dumps(d)

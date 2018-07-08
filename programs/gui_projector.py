import wx
import cv2
import time
import RPCClient
import logging
import numpy as np
import math
import json
import zmq
from threading import Thread
from wx.lib.pubsub import pub

logging.basicConfig(level=logging.INFO)

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

context = zmq.Context()

class Example(wx.Frame):
    ID_TIMER = 1
    GRAPHICS_TIMER = 2
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(CAM_WIDTH, CAM_HEIGHT))

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # self.Centre()
        self.Show()
        self.Maximize(True)

        self.i = 0
        self.bmp = None
        self.dots = []
        self.corners = []
        self.papers = []
        self.projector_calibration = []
        self.projection_matrix = None
        self.draw_wishes = {}
        self.latestCount = None

        self.sub_socket = context.socket(zmq.SUB)
        # self.sub_socket.set_hwm(5)
        self.sub_socket.connect("tcp://localhost:5556")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "WISH[DRAW/")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "DEATH[")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "CLAIM[global/dots]")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "CLAIM[global/papers]")
        # self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "CLAIM[global/corners]")
        # self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "CLAIM[global/projector_calibration]")
        # self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "CLAIM[global/dtpcount]")
        time.sleep(1)
        # self.mainLoop()

        self.timer = wx.Timer(self, Example.ID_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Example.ID_TIMER)

        self.graphics_timer = wx.Timer(self, Example.GRAPHICS_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnGraphicsTimer, id=Example.GRAPHICS_TIMER)

        fps = 10
        self.timer.Start(1000./fps)

        graphics_fps = 10
        self.graphics_timer.Start(1000./graphics_fps)

        self.lastPaint = time.time()
        self.bigStart = time.time()

    def OnGraphicsTimer(self, event):
        self.Refresh()

    def OnTimer(self, event):
        start = time.time()
        self.bigStart = time.time()
        # logging.error("loop")
        wishes = []
        deaths = []
        old_calibration = self.projector_calibration
        received_any_value = False
        while True:
            try:
                string = self.sub_socket.recv_string(flags=zmq.NOBLOCK)
                received_any_value = True
                event_type = val = string.split('[', 1)[0]  # WISH, CLAIM
                if event_type in ["WISH", "CLAIM"]:
                    key = (string.split(']', 1)[0]).split('/', 1)[1]
                    val = string.split(']', 1)[1]
                    if key == "dtpcount":
                        logging.error("DTPCOUNT:")
                        logging.error(string)
                    json_val = json.loads(val)
                    if event_type == "WISH":
                        wishes.append((key, json_val))
                    elif event_type == "CLAIM":
                        if key == "dots":
                            self.dots = json_val
                        elif key == "corners":
                            self.corners = json_val
                        elif key == "papers":
                            self.papers = json_val
                        elif key == "projector_calibration":
                            self.projector_calibration = json_val
                        elif key == "dtpcount":
                            self.latestCount = json_val
                elif event_type == "DEATH":
                    program_id = (string.split(']', 1)[0]).split('[', 1)[1]
                    deaths.append(program_id)
            except zmq.Again:
                logging.error("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ AGAIN" + str(received_any_value))
                break

        self.onWish(wishes)
        self.onProgramDeath(deaths)

        if old_calibration != self.projector_calibration:
            if self.projector_calibration and len(self.projector_calibration) is 4:
                logging.error("RECAL PROJECTION MATRIX")
                pts1 = np.float32(self.projector_calibration)
                pts2 = np.float32([[0,0],[CAM_WIDTH,0],[CAM_WIDTH,CAM_HEIGHT],[0,CAM_HEIGHT]])
                self.projection_matrix = cv2.getPerspectiveTransform(pts1, pts2)
                # logging.info("CONVERT PERSPECTIVE")
                # logging.info(self.projection_matrix)
                # logging.info(np.float32(self.projector_calibration))
                #
                # dst = cv2.perspectiveTransform(np.array([np.float32(self.projector_calibration)]), self.projection_matrix)
                # logging.info("IDENTITY?")
                # logging.info(dst)
                # logging.info(list(map(lambda x: [int(x[0]), int(x[1])], dst[0])))

        end = time.time()
        print(1000*(end - start), "ms", 1.0/(end - start), "fps")


    def OnPaint(self, e):
        now = time.time()
        print(1.0/(now - self.lastPaint), "fps for paint")
        self.lastPaint = time.time()

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(wx.Colour(0,0,0)))
        dc.Clear()
        dc.SetTextForeground(wx.Colour(255,255,255))
        dc.SetBrush(wx.Brush())
        font =  dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)

        if self.latestCount:
            dc.DrawText(str(self.latestCount), 10, 10)

        # if self.bmp:
        #     dc.DrawBitmap(self.bmp, 0, 0)
        if self.dots:
            for dot in self.dots:
                dc.SetBrush(wx.Brush(wx.Colour(dot["color"][0], dot["color"][1], dot["color"][2])))
                dc.SetPen(wx.Pen(wx.Colour(255, 255, 0)))
                s = 3
                dc.DrawEllipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)

        paper_draw_wishes = {}
        if self.draw_wishes:
            for wish_source in self.draw_wishes:
                for target in self.draw_wishes[wish_source]:
                    target_commands = self.draw_wishes[wish_source][target]
                    if target not in paper_draw_wishes:
                        paper_draw_wishes[target] = []
                    paper_draw_wishes[target].extend(target_commands)
        logging.error(paper_draw_wishes)

        for i, target in enumerate(paper_draw_wishes):
            dc.DrawText(target + ": " + json.dumps(paper_draw_wishes[target]), 10, 10+16*i)

        self.draw_global_wishes(gc, paper_draw_wishes.get("global"))

        if self.papers:
            for paper in self.papers:
                dc.SetPen(wx.NullPen)
                dc.SetBrush(wx.Brush(wx.Colour(0, 255, 0, 99)))  # transparent green
                if len(paper["corners"]) == 4:
                    tri1 = []
                    tri2 = []
                    for corner in paper["corners"]:
                        if corner["CornerId"] in [0,1,2]:
                            tri1.append(corner)
                        if corner["CornerId"] in [2,3,0]:
                            tri2.append(corner)

                    # Highlight full shape:
                    # dc.DrawPolygon(self.project(list(map(lambda c: (c["x"], c["y"]), tri1))))
                    # dc.DrawPolygon(self.project(list(map(lambda c: (c["x"], c["y"]), tri2))))

                    self.draw_paper(gc, paper, paper_draw_wishes.get(paper["id"]))
                if len(paper["corners"]) == 3:
                    tri1 = paper["corners"]
                    pts = self.project(list(map(lambda c: [c["x"], c["y"]], tri1)))
                    # dc.DrawPolygon(pts)
                for corner in paper["corners"]:
                    textPt = self.project([(corner["x"], corner["y"])])[0]
                    # dc.DrawText(paper["id"] + ": " + str(corner["CornerId"]), textPt[0], textPt[1])
        # if self.corners:
        #     for corner in self.corners:
        #         dc.SetPen(wx.NullPen)
        #         dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        #         dc.DrawText(corner["colorString"], corner["corner"]["x"], corner["corner"]["y"]+20)
        #         step = 10
        #         s = 3
        #         for i, c in enumerate(corner["colorString"]):
        #             raw_color = corner["rawColorsList"][i]
        #             dc.SetBrush(wx.Brush(wx.Colour(*raw_color)))
        #             dc.DrawEllipse(corner["corner"]["x"]+i*step-s, corner["corner"]["y"]-s, s*2, s*2)
        #             if c == '0':
        #                 dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        #             elif c == '1':
        #                 dc.SetBrush(wx.Brush(wx.Colour(0, 255, 0)))
        #             elif c == '2':
        #                 dc.SetBrush(wx.Brush(wx.Colour(0, 0, 255)))
        #             elif c == '3':
        #                 dc.SetBrush(wx.Brush(wx.Colour(200, 200, 200)))
        #             dc.DrawEllipse(corner["corner"]["x"]+i*step-s, corner["corner"]["y"]+10-s, s*2, s*2)

        end = time.time()
        print(1000*(end - now), "ms", 1.0/(end - now), "fps to do paint stuff")

    def dist(self, p1, p2):
        return math.sqrt( (p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2 )

    def draw_global_wishes(self, gc, commands):
        if not commands:
            return
        self.draw_commands(gc, commands, CAM_WIDTH)

    def draw_commands(self, gc, draw_commands, width):
        paper_font = wx.Font(int(width/10), wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD)
        paper_font_color = wx.Colour(255,255,255)

        # img = wx.Image("./test_image.png", wx.BITMAP_TYPE_ANY)
        # bmp = gc.CreateBitmapFromImage(img)
        # gc.DrawBitmap(bmp, 100, 0, img.GetWidth(), img.GetHeight())
        gc.SetFont(paper_font, paper_font_color)
        # gc.DrawText("Paper "+str(paper["id"]), 0, 0)

        last_pen = wx.Pen("white")
        last_stroke_width = 1
        last_brush = wx.Brush("blue")
        gc.SetPen(last_pen)
        gc.SetBrush(last_brush)

        if draw_commands:
            print(draw_commands)
            for command in draw_commands:
                command_type = command.get("type")
                opt = command.get("options")
                if command_type == "rectangle":
                    if opt:
                        gc.DrawRectangle(opt["x"], opt["y"], opt["w"], opt["h"])
                elif command_type == "ellipse":
                    if opt:
                        gc.DrawEllipse(opt["x"], opt["y"], opt["w"], opt["h"])
                elif command_type == 'text':
                    if opt:
                        print("DRAWING TEXT")
                        lines = opt["text"].split("\n")
                        line_height = paper_font.GetPixelSize().GetHeight() * 1.3
                        for i, l in enumerate(lines):
                            gc.DrawText(l, opt["x"], opt["y"] + i * line_height)
                    else:
                        print("would draw text but missing opt")
                elif command_type == 'line':
                    if opt and len(opt) == 4:
                        # actually only drawing 1 line
                        gc.DrawLines([wx.Point2D(opt[0], opt[1]), wx.Point2D(opt[2], opt[3])])
                    else:
                        print("bad line")
                        print(opt)
                elif command_type == 'fill':
                    if opt:
                        if type(opt) is str:
                            last_brush = wx.Brush(opt)  # color name like "blue"
                        elif len(opt) is 3:
                            last_brush = wx.Brush(wx.Colour(opt[0], opt[1], opt[2]))  # RGB
                        else:
                            last_brush = wx.Brush(wx.Colour(opt[0], opt[1], opt[2], opt[3]))  # RGBA
                        gc.SetBrush(last_brush)
                elif command_type == 'stroke':
                    if opt:
                        if type(opt) is str:
                            last_pen = wx.Pen(opt)  # color name like "blue"
                        elif len(opt) is 3:
                            last_pen = wx.Pen(wx.Colour(opt[0], opt[1], opt[2]))  # RGB
                        else:
                            last_pen = wx.Pen(wx.Colour(opt[0], opt[1], opt[2], opt[3]))  # RGBA
                        last_pen.SetWidth(last_stroke_width)
                        gc.SetPen(last_pen)
                elif command_type == 'nostroke':
                    last_pen.SetStyle(wx.PENSTYLE_TRANSPARENT)
                    gc.SetPen(last_pen)
                elif command_type == 'nofill':
                    last_brush.SetStyle(wx.BRUSHSTYLE_TRANSPARENT)
                    gc.SetBrush(last_brush)
                elif command_type == 'strokewidth':
                    if opt:
                        last_stroke_width = int(opt)
                        last_pen.SetWidth(last_stroke_width)
                        gc.SetPen(last_pen)
                elif command_type == 'fontsize':
                    if opt:
                        paper_font = wx.Font(opt, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD)
                        gc.SetFont(paper_font, paper_font_color)
                elif command_type == 'fontcolor':
                    if opt and len(opt) == 3:
                        paper_font_color = wx.Colour(opt[0], opt[1], opt[2])
                        gc.SetFont(paper_font, paper_font_color)
                elif command_type == 'push':
                    gc.PushState()
                elif command_type == 'pop':
                    gc.PushState()
                elif command_type == 'translate':
                    if opt:
                        gc.Translate(opt["x"], opt["y"])
                elif command_type == 'rotate':
                    if opt:
                        gc.Rotate(opt)
                elif command_type == 'scale':
                    if opt:
                        gc.Translate(opt["x"], opt["y"])
                else:
                    print("Unrecognized command:")
                    print(command)

    def draw_paper(self, gc, paper, draw_commands):
        tl = None
        tr = None
        bl = None
        for corner in paper["corners"]:
            if corner["CornerId"] == 0:
                tl = self.project2(corner)
            elif corner["CornerId"] == 1:
                tr = self.project2(corner)
            elif corner["CornerId"] == 3:
                bl = self.project2(corner)
        paper_width = self.dist(tl, tr)
        paper_height = self.dist(tl, bl)
        paper_origin = tl
        logging.error(paper_origin)
        paper_angle = math.atan2(tr["y"] - tl["y"], tr["x"] - tl["x"])

        gc.BeginLayer(1.0)

        gc.PushState()
        gc.Translate(paper_origin["x"], paper_origin["y"])
        gc.Rotate(paper_angle)

        gc.SetPen(wx.Pen("red", 3))
        # gc.SetBrush(wx.Brush("blue"))

        # gc.DrawRectangle(0, 0, paper_width, paper_height)

        self.draw_commands(gc, draw_commands, paper_width)

        gc.PopState()
        gc.EndLayer()

    def project(self, pts):
        if self.projection_matrix is not None:
            # return pts
            dst = cv2.perspectiveTransform(np.array([np.float32(pts)]), self.projection_matrix)
            return list(map(lambda x: [int(x[0]), int(x[1])], dst[0]))
        # logging.error("MISSING PROJECTION MATRIX FOR PAPERS!")
        return pts

    def project2(self, _pt):
        pt = _pt.copy()
        # logging.error("1:")
        # logging.error(_pt)
        # logging.error("2:")
        # logging.error(pt)
        # return pt
        if self.projection_matrix is not None:
            # return pts
            pts = [(pt["x"], pt["y"])]
            dst = cv2.perspectiveTransform(np.array([np.float32(pts)]), self.projection_matrix)
            pt["x"] = int(dst[0][0][0])
            pt["y"] = int(dst[0][0][1])
            return pt
        # logging.error("MISSING PROJECTION MATRIX FOR PAPERS!")
        return pt

    def onWish(self, wishes):
        for wish in wishes:
            source = wish[0]
            val = wish[1]
            logging.error("onWish")
            logging.error(source)
            logging.error(val)
            if val == "DEATH":
                if source in self.draw_wishes:
                    del self.draw_wishes[source]
            else:
                for target in val:
                    draw_commands = val[target]
                    if source not in self.draw_wishes:
                        self.draw_wishes[source] = {}
                    self.draw_wishes[source][target] = draw_commands

    def onProgramDeath(self, deaths):
        for program_id in deaths:
            logging.error("on_program_death")
            logging.error(program_id)
            if program_id in self.draw_wishes:
                del self.draw_wishes[program_id]


if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()

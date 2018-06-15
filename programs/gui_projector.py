import wx
import cv2
import time
import RPCClient
import logging
import numpy as np
import math
import json

logging.basicConfig(level=logging.INFO)

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

class Example(wx.Frame):
    ID_TIMER = 1
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
        self.draw_wishes = []

        self.M = RPCClient.RPCClient()

        self.timer = wx.Timer(self, Example.ID_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Example.ID_TIMER)

        fps = 20
        self.timer.Start(1000./fps)

    def OnPaint(self, e):
        # dc = wx.PaintDC(self)
        # logging.info(self.i)
        # dc.DrawLine(50, 60 + self.i, 190, 60)
        # dc.DrawEllipse(20, 20, 90, 60)
        # dc.DrawRectangle(250, 200, 60, 60)
        #
        # font =  dc.GetFont()
        # font.SetWeight(wx.FONTWEIGHT_BOLD)
        # dc.SetFont(font)
        # dc.DrawText('Historical Prices', 90, 235)

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(wx.Colour(0,0,0)))
        dc.Clear()
        dc.SetTextForeground(wx.Colour(255,255,255))
        dc.SetBrush(wx.Brush())
        font =  dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
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
            for wish in self.draw_wishes:
                wish_options = wish.get("options")
                if type(wish_options) is dict:
                    for target in wish_options:
                        target_commands = wish_options[target]
                        if target not in paper_draw_wishes:
                            paper_draw_wishes[target] = []
                        paper_draw_wishes[target].extend(target_commands)
                else:
                    print("TYPE ISN't DICT")
                    print(wish)
            self.draw_global_wishes(paper_draw_wishes.get("global"))

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
                    dc.DrawPolygon(pts)
                for corner in paper["corners"]:
                    textPt = self.project([(corner["x"], corner["y"])])[0]
                    dc.DrawText(paper["id"] + ": " + str(corner["CornerId"]), textPt[0], textPt[1])
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

    def dist(self, p1, p2):
        return math.sqrt( (p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2 )

    def draw_global_wishes(self, commands):
        if not commands:
            return
        print("TODO")

    def draw_paper(self, gc, paper, draw_commands):
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
        paper_width = self.dist(tl, tr)
        paper_height = self.dist(tl, bl)
        paper_origin = tl
        paper_angle = math.atan2(tr["y"] - tl["y"], tr["x"] - tl["x"])
        paper_font = wx.Font(int(paper_width/10), wx.DEFAULT, wx.NORMAL, wx.BOLD)
        paper_font_color = wx.Colour(255,255,255)

        gc.BeginLayer(1.0)

        gc.PushState()
        gc.Translate(paper_origin["x"], paper_origin["y"])
        gc.Rotate(paper_angle)

        gc.SetPen(wx.Pen("red", 3))
        # gc.SetBrush(wx.Brush("blue"))

        gc.DrawRectangle(0, 0, paper_width, paper_height)

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
                        gc.DrawText(opt["text"], opt["x"], opt["y"])
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
                        wx.SetBrush(last_brush)
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
                        paper_font = wx.Font(opt, wx.DEFAULT, wx.NORMAL, wx.BOLD)
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

        gc.PopState()
        gc.EndLayer()

    def project(self, pts):
        if self.projection_matrix is not None:
            return pts
            # dst = cv2.perspectiveTransform(np.array([np.float32(pts)]), self.projection_matrix)
            # return list(map(lambda x: [int(x[0]), int(x[1])], dst[0]))
        logging.error("MISSING PROJECTION MATRIX FOR PAPERS!")
        return None

    def OnTimer(self, event):
        if event.GetId() == Example.ID_TIMER:

            start = time.time()

            wishes = self.M.get_wishes_by_type("DRAW")
            # logging.info("PROJECTOR: " + str(wishes))
            self.draw_wishes = []
            for wish in wishes:
                draw_options = {}
                try:
                    draw_options = json.loads(wish.get("action"))
                except:
                    pass
                self.draw_wishes.append({
                    "source": wish["source"],
                    "options": draw_options
                })
            # logging.info("PROJECTION: " + str(result))
            # self.M.clear_wishes({"type": "DRAW"})
            # self.i += 2
            # wxImg = wx.Image()
            # image_string = self.M.get_image()
            # # wxImg.SetData(image_string)
            # wxImg = wx.ImageFromBuffer(CAM_WIDTH, CAM_HEIGHT, image_string)
            # logging.info("got frame")

            def receiveDots(dots):
                self.dots = dots
            dots = self.M.when("global", "dots", receiveDots)
            # logging.info("got dots %s" % len(self.dots))

            def receivePapers(papers):
                self.papers = papers
            self.M.when("global", "papers", receivePapers)
            # if self.papers:
            #     logging.info("got papers %s" % len(self.papers))

            def receiveCorners(corners):
                self.corners = corners
            self.M.when("global", "corners", receiveCorners)
            # if self.corners:
            #     logging.info("got corners %s" % len(self.corners))

            def receiveProjectorCalibration(cal):
                self.projector_calibration = cal
            self.M.when("global", "projector_calibration", receiveProjectorCalibration)
            # logging.info("got projector_calibration %s" % self.projector_calibration)

            if self.projector_calibration and len(self.projector_calibration) is 4:
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

            # self.bmp = wxImg.ConvertToBitmap()

            self.Refresh()

            end = time.time()
            print(end - start, 1.0/(end - start), "fps")
        else:
            event.Skip()

if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()

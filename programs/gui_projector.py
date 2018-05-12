import wx
import cv2
import time
import RPCClient
import logging
import numpy as np

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

        fps = 4
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
        dc.SetBackground(wx.Brush(wx.Colour(0,0,0)))
        dc.Clear()
        dc.SetTextForeground(wx.Colour(255,255,255))
        dc.SetBrush(wx.Brush())
        font =  dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        # if self.bmp:
        #     dc.DrawBitmap(self.bmp, 0, 0)
        # for dot in self.dots:
        #     dc.SetBrush(wx.Brush(wx.Colour(dot["color"][0], dot["color"][1], dot["color"][2])))
        #     dc.SetPen(wx.Pen(wx.Colour(255, 255, 0)))
        #     s = 3
        #     dc.DrawEllipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)
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
                    dc.DrawPolygon(self.project(list(map(lambda c: (c["x"], c["y"]), tri1))))
                    dc.DrawPolygon(self.project(list(map(lambda c: (c["x"], c["y"]), tri2))))
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
        if self.draw_wishes:
            for i, w in enumerate(self.draw_wishes):
                dc.DrawText(w, 20, 20 + 20*i)

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
            self.draw_wishes = ["test"]
            for wish in wishes:
                self.draw_wishes.append("%s %s" % (wish["source"], wish["action"],))
            # logging.info("PROJECTION: " + str(result))
            self.M.clear_wishes({"type": "DRAW"})
            # self.i += 2
            # wxImg = wx.Image()
            image_string = self.M.get_image()
            # wxImg.SetData(image_string)
            wxImg = wx.ImageFromBuffer(CAM_WIDTH, CAM_HEIGHT, image_string)
            logging.info("got frame")

            def receiveDots(dots):
                self.dots = dots
            dots = self.M.when("global", "dots", receiveDots)
            logging.info("got dots %s" % len(self.dots))

            def receivePapers(papers):
                self.papers = papers
            self.M.when("global", "papers", receivePapers)
            if self.papers:
                logging.info("got papers %s" % len(self.papers))

            def receiveCorners(corners):
                self.corners = corners
            self.M.when("global", "corners", receiveCorners)
            if self.corners:
                logging.info("got corners %s" % len(self.corners))

            def receiveProjectorCalibration(cal):
                self.projector_calibration = cal
            self.M.when("global", "projector_calibration", receiveProjectorCalibration)
            logging.info("got projector_calibration %s" % self.projector_calibration)

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

            self.bmp = wxImg.ConvertToBitmap()

            self.Refresh()

            end = time.time()
            print(end - start)
        else:
            event.Skip()

if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()

import wx
import RPCClient
import logging

logging.basicConfig(level=logging.INFO)

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

class Example(wx.Frame):
    ID_TIMER = 1
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(CAM_WIDTH, CAM_HEIGHT))

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Centre()
        self.Show()

        self.i = 0
        self.bmp = None
        self.dots = []
        self.papers = []

        self.M = RPCClient.RPCClient()

        self.timer = wx.Timer(self, Example.ID_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Example.ID_TIMER)

        fps = 10
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
        if self.bmp:
            dc.DrawBitmap(self.bmp, 0, 0)
        for dot in self.dots:
            dc.SetBrush(wx.Brush(wx.Colour(dot["color"][0], dot["color"][1], dot["color"][2])))
            dc.SetPen(wx.Pen(wx.Colour(255, 255, 0)))
            s = 3
            dc.DrawEllipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)
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
                dc.DrawPolygon(list(map(lambda c: (c["x"], c["y"]), tri1)))
                dc.DrawPolygon(list(map(lambda c: (c["x"], c["y"]), tri2)))
            if len(paper["corners"]) == 3:
                tri1 = paper["corners"]
                dc.DrawPolygon(list(map(lambda c: (c["x"], c["y"]), tri1)))
            font =  dc.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            dc.SetFont(font)
            for corner in paper["corners"]:
                dc.DrawText(paper["id"] + ": " + str(corner["CornerId"]), corner["x"], corner["y"])

    def OnTimer(self, event):
        if event.GetId() == Example.ID_TIMER:
            # wishes = self.M.get_wishes_by_type("DRAW")
            # # logging.info("PROJECTOR: " + str(wishes))
            # result = {}
            # for wish in wishes:
            #     result[wish["source"]] = result.get(wish["source"], '') + wish["action"]
            # logging.info("PROJECTION: " + str(result))
            # self.M.clear_wishes({"type": "DRAW"})
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
            logging.info("got papers %s" % len(self.papers))

            self.bmp = wxImg.ConvertToBitmap()

            self.Refresh()
        else:
            event.Skip()

if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()

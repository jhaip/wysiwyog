import wx
import RPCClient
import logging

logging.basicConfig(level=logging.INFO)

class Example(wx.Frame):
    ID_TIMER = 1
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(1280, 720))

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Centre()
        self.Show()

        self.i = 0
        self.bmp = None
        self.dots = []

        self.M = RPCClient.RPCClient()

        self.timer = wx.Timer(self, Example.ID_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Example.ID_TIMER)

        fps = 1
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
            wxImg = wx.ImageFromBuffer(1280, 720, image_string)  # TODO: don't harcode size
            logging.info("got frame")
            def receiveDots(dots):
                self.dots = dots
            dots = self.M.when("global", "dots", receiveDots)
            logging.info("got dots %s" % len(self.dots))
            self.bmp = wxImg.ConvertToBitmap()

            self.Refresh()
        else:
            event.Skip()

if __name__ == '__main__':
    app = wx.App()
    Example(None, 'Line')
    app.MainLoop()

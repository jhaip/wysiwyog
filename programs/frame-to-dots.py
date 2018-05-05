# Example from https://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
import wx
import cv2
import time
import json
import RPCClient

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=1):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)
        self.dots = []

        self.M = RPCClient.RPCClient()

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)
        for dot in self.dots:
            dc.SetBrush(wx.Brush(wx.Colour(dot["color"][0], dot["color"][1], dot["color"][2])))
            # dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
            dc.SetPen(wx.Pen(wx.Colour(255, 0, 0)))
            s = 3
            dc.DrawEllipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:

            start = time.time()
            params = cv2.SimpleBlobDetector_Params()
            params.filterByCircularity = True
            params.minCircularity = 0.9
            params.filterByArea = True
            params.minArea = 25
            params.filterByInertia = False
            is_v2 = cv2.__version__.startswith("2.")
            if is_v2:
                detector = cv2.SimpleBlobDetector(params)
            else:
                detector = cv2.SimpleBlobDetector_create(params)

            keypoints = detector.detect(frame)

            # print(self.keypoints)
            def keypointMapFunc(keypoint):
                color = frame[int(keypoint.pt[1]), int(keypoint.pt[0])]
                return {
                    "x": int(keypoint.pt[0]),
                    "y": int(keypoint.pt[1]),
                    "color": [int(color[2]), int(color[1]), int(color[0])]
                }
            self.dots = list(map(keypointMapFunc, keypoints))
            # print(self.dots)
            self.M.claim("global", "dots", self.dots)

            end = time.time()
            print(end - start)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)

            img = wx.Bitmap.ConvertToImage( self.bmp )
            img_str = img.GetData()
            self.M.set_image(img_str)

            self.Refresh()


capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()

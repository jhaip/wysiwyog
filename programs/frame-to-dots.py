# Example from https://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
import wx
import cv2
import time
import json
import RPCClient
import logging

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=10):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)
        self.dots = []

        self.projector_calibration_state = None


        self.M = RPCClient.RPCClient()

        def receiveProjectorCalibration(cal):
            if cal:
                self.projector_calibration = cal
            else:
                logging.error("no projector cal, using default")
                self.projector_calibration = [(50, 50), (CAM_WIDTH-50, 50),
                                              (CAM_WIDTH-50, CAM_HEIGHT-50),
                                              (50, CAM_HEIGHT-50)]
                self.M.claim("global", "projector_calibration", self.projector_calibration)
        self.M.when("global", "projector_calibration", receiveProjectorCalibration)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(wx.EVT_LEFT_UP, self.onClick)
        self.SetFocus()


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.SetBrush(wx.Brush())
        font =  dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)

        dc.DrawBitmap(self.bmp, 0, 0)

        for dot in self.dots:
            dc.SetBrush(wx.Brush(wx.Colour(dot["color"][0], dot["color"][1], dot["color"][2])))
            # dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
            dc.SetPen(wx.Pen(wx.Colour(255, 0, 0)))
            s = 3
            dc.DrawEllipse(int(dot["x"])-s, int(dot["y"])-s, s*2, s*2)

        dc.SetBrush(wx.Brush(wx.Colour(0,255,255), style=wx.BRUSHSTYLE_TRANSPARENT))
        dc.SetPen(wx.Pen(wx.Colour(0,0,255)))
        dc.DrawPolygon(self.projector_calibration)

        if self.projector_calibration_state is not None:
            pt = self.projector_calibration[self.projector_calibration_state]
            dc.SetBrush(wx.Brush(wx.Colour(0,255,255), style=wx.BRUSHSTYLE_TRANSPARENT))
            dc.SetPen(wx.Pen(wx.Colour(255, 255, 255)))
            s = 3
            dc.DrawEllipse(int(pt[0])-s, int(pt[1])-s, s*2, s*2)
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0)))
            s = s + 1
            dc.DrawEllipse(int(pt[0])-s, int(pt[1])-s, s*2, s*2)
            dc.SetPen(wx.Pen(wx.Colour(255, 255, 255)))
            s = s + 1
            dc.DrawEllipse(int(pt[0])-s, int(pt[1])-s, s*2, s*2)
            dc.DrawText("EDITING CORNER " + str(self.projector_calibration_state), CAM_WIDTH/2, CAM_HEIGHT/2)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:

            start = time.time()
            params = cv2.SimpleBlobDetector_Params()
            params.minThreshold = 10
            params.maxThreshold = 240
            params.filterByCircularity = True
            params.minCircularity = 0.5
            params.filterByArea = True
            params.minArea = 12
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

    def moveCurrentCalibrationPointRel(self, dx, dy):
        if self.projector_calibration_state is not None:
            prev = self.projector_calibration[self.projector_calibration_state]
            next = (prev[0] + dx, prev[1] + dy)
            self.projector_calibration[self.projector_calibration_state] = next
            self.M.claim("global", "projector_calibration", self.projector_calibration)

    def moveCurrentCalibrationPoint(self, pt):
        if self.projector_calibration_state is not None:
            self.projector_calibration[self.projector_calibration_state] = (pt[0], pt[1])
            self.M.claim("global", "projector_calibration", self.projector_calibration)

    def changeCurrentCalibrationPoint(self, key):
        if key == '`':
            self.projector_calibration_state = None
        elif key in ['1', '2', '3', '4']:
            self.projector_calibration_state = int(key)-1

    def OnKeyDown(self, event=None):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_UP:
            self.moveCurrentCalibrationPointRel(0, -1)
        elif keyCode == wx.WXK_RIGHT:
            self.moveCurrentCalibrationPointRel(1, 0)
        elif keyCode == wx.WXK_DOWN:
            self.moveCurrentCalibrationPointRel(0, 1)
        elif keyCode == wx.WXK_LEFT:
            self.moveCurrentCalibrationPointRel(-1, 0)
        else:
            unicodeKey = chr(event.GetUnicodeKey())
            if unicodeKey in ['`', '1', '2', '3', '4']:
                self.changeCurrentCalibrationPoint(unicodeKey)

    def onClick(self, event=None):
        if event:
            pt = event.GetPosition()
            self.moveCurrentCalibrationPoint(pt)


capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()

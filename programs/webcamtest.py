# Example from https://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
import wx
import cv2
import time
import json
import RPCClient

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
        self.i = 0

        self.M = RPCClient.RPCClient()

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)

            self.i += 1
            if True: # self.i % 10 == 0:
                # start = time.time()
                img = wx.Bitmap.ConvertToImage( self.bmp )
                img_str = img.GetData()
                self.M.set_image(img_str)
                # img_str2 = json.loads(json.dumps({"img": str(img_str)}))
                # print("hello")
                # end = time.time()
                # print(end - start)
                # print(len(str(img_str)))

            self.Refresh()


capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()

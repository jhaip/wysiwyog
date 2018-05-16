# WYSIWYOG

What you see if what you ought get.

---

**4/29/18**

A [Stack Overflow post](https://stackoverflow.com/questions/35009984/get-stream-from-webcam-with-opencv-and-wxpython) suggested using the [VLC Python bindings](https://wiki.videolan.org/Python_bindings) to show a webcam video in wxPython.
wxPython also wx.Image() with methods to convert to and from a String version of the image.
This could be nice for transmitting the webcam video via ZeroMQ.

* [wxPython - Working with Images](https://wiki.wxpython.org/WorkingWithImages)
* [ZeroMQ receive from multiple sockets in Python](http://zguide.zeromq.org/py:msreader)
* [Create an wx.Image from array](https://stackoverflow.com/questions/20033749/python-image-object-to-wxpython)

Can't set a Core profile for OpenGL 3.2+ with wxPython :(
According to [this](https://git.fmrib.ox.ac.uk/fsl/fslpy/blob/a38d81b13d428fefc77487d0072d4a2b58210edb/fsl/fslview/slicecanvas.py)

Switching to go because OpenGL and shader support in wxPython is a mess.
[helpful link about OpenGL, glfw, and shaders in Go](https://kylewbanks.com/blog/tutorial-opengl-with-golang-part-1-hello-opengl)

[Go ZeroMQ v4 bindings](https://github.com/pebbe/zmq4)
[hwclient](https://github.com/pebbe/zmq4/blob/master/examples/hwclient.go)

**5/5/18**

May be useful for speeding up Python OpenCV SimpleBlobDetector using GetContours instead with `faster` option. https://stackoverflow.com/questions/42203898/python-opencv-blob-detection-or-circle-detection

Projection Transform: https://docs.opencv.org/3.4.0/da/d6e/tutorial_py_geometric_transformations.html

**5/12/18**

Reducing lag on video:
* https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
* https://github.com/npinto/opencv/blob/master/samples/python2/video_threaded.py

**5/15/18**

https://github.com/tutorcruncher/pydf

```
docker run -rm -p 8000:80 -d samuelcolvin/pydf
curl -d '<h1>this is html</h1>' -H "pdf-orientation: landscape" http://localhost:8000/generate.pdf > created.pdf
open "created.pdf"
```

```
services:
  pdf:
    image: samuelcolvin/pydf
```

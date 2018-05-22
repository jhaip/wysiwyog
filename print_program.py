import requests
from string import Template

# print PDF on MacOS: lpr 1.pdf

program_name = "123 - Fox catcher"
source_code = """
import time
import zmq
import logging
import json
import psutil
import uuid
import sqlite3
import random
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

context = zmq.Context()
string_socket = context.socket(zmq.REP)
"""

url = "http://localhost:8011/generate.pdf"
headers = {
    "pdf-orientation": "landscape"
}
html_base = '''
<html>
<head><style>
#target{
    width: 50px;
    height: 50px;
    background-color: #000;
    border-radius: 50%;
    margin: 12px;
}
.corner {
  position: absolute;
}
.top {
  top: 0;
}
.bottom {
  bottom: 0;
}
.right {
  right: 0;
}
.right div {
  float: right;
}
.left {
  left: 0;
}
.left div {
  float: left;
}
.clear {
  clear: both;
  float: none;
}
#code {
  position: absolute;
  left: 100px;
  right: 100px;
  top: 74px;
  bottom: 74px;
  overflow: hidden;
  font-size: 12px;
  line-height: 1.3;
  font-family: monospace;
}
#title {
  position: absolute;
  bottom: 12px;
  left: 50%;
  width: 240px;
  margin-left: -120px;
  text-align: center;
  font-size: 16px;
  font-family: san-serif;
}
</style></head>
<body>
<div class="corner top left">
  <div>
    <div id="target" style="background-color: #F00"></div>
    <div id="target" style="background-color: #0F0"></div>
    <div id="target" style="background-color: #00F"></div>
    <div id="target" style="background-color: #F00"></div>
  </div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
</div>
<div class="corner top right">
  <div>
    <div id="target" style="background-color: #F00"></div>
    <div id="target" style="background-color: #0F0"></div>
    <div id="target" style="background-color: #00F"></div>
    <div id="target" style="background-color: #F00"></div>
  </div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
</div>
<div class="corner bottom right">
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div>
    <div id="target" style="background-color: #F00"></div>
    <div id="target" style="background-color: #0F0"></div>
    <div id="target" style="background-color: #00F"></div>
    <div id="target" style="background-color: #F00"></div>
  </div>
  <div class="clear"></div>
</div>
<div class="corner bottom left">
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div id="target" style="background-color: #000"></div>
  <div class="clear"></div>
  <div>
    <div id="target" style="background-color: #F00"></div>
    <div id="target" style="background-color: #0F0"></div>
    <div id="target" style="background-color: #00F"></div>
    <div id="target" style="background-color: #F00"></div>
  </div>
  <div class="clear"></div>
</div>

<pre id="code">
$code
</pre>

<div id="title">
$title
</div>
</body>
</html>
'''
template = Template(html_base)
html = template.substitute({ 'code': source_code, 'title': program_name})

r = requests.post(url, data=html, headers=headers)
filename = "1.pdf"
with open(filename, 'wb') as f:
    f.write(r.content)

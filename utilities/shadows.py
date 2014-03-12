"""
generate 64 tiles in gradient from black to white
use ordered dithering to halftone them
"""

from subprocess import call
import os
import math


tempfile = "blank.png"

w = 16
h = 16

# make temp canvas 
cmd = "convert", "-size", "{}x{}".format(w, h), "canvas:white", "blank.png"
call(cmd)

x = 0.0
i = 0
while x < 100:
    v = math.ceil(x)

    cmd = "convert", "blank.png", "+level", "%{},%{}".format(v,v), \
          "+matte", "solid.png"
    call(cmd)

    cmd = "convert", "solid.png", "-ordered-dither", "o8x8", \
          "dither{:02d}.png".format(i)

    call(cmd)
    x += 100.0/64
    i += 1

cmd = "montage", "dither*", "-tile", "64x1", "-geometry", \
      "{}x{}+0+0".format(w,h), "grads.png"

call(cmd)

for x in range(0,64):
    os.unlink("dither{:02d}.png".format(x))

os.unlink(tempfile)
os.unlink("solid.png")

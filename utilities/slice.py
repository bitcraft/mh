#!/usr/bin/env python

"""
slice up an image and save it as a file readable by the bigimage
class

you should have an idea what resolution your game will be running at
in order to make good use of the sprites.

the images must be a power of 2.  16 is the smallest tile allowed.
larger tiles, such as 512x512 are supported, but keep in mind that
the memory use of the game will be much higher.

i reccommend 64x64 or 128x128 for large files.

USAGE:
slice.py image_file prefix

prefix will be the first part of each image's file name

"""

from struct import pack
import sys

from cStringIO import StringIO


def encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Convert positive integer to a base36 string."""

    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    # Special case for zero
    if number == 0:
        return alphabet[0]
 
    base36 = ''
 
    sign = ''
    if number < 0:
        sign = '-'
        number = - number
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36
 
def decode(number):
    return int(number, 36)

try:
    from PIL import Image
except:
    print("cannot import PIL")
    print("PIL must be installed")
    sys.exit()

# make sure there are enough arguments:
if len(sys.argv) != 4:
    print("USAGE:")
    print("slice.py image_file prefix tilesize")
    print
    print("prefix will be the first part of each image's file name")
    sys.exit()

tilesizeX, tilesizeY = int(sys.argv[3]), int(sys.argv[3])
im = Image.open(sys.argv[1])
prefix = sys.argv[2]
x0, y0, x1, y1 = im.getbbox()

def blowup():
    mapx = x1 / tilesizeX
    mapy = y1 / tilesizeX

    fh = open("map.dat", "rb")
    for pos in range(mapx * mapy):
        pass

# slice into a bunch of files
def intoFiles():
    for x in range(x0, x1, tilesizeX):
        for y in range(y0, y1, tilesizeY):
            tile = im.crop((x, y, x + tilesizeX, y + tilesizeY))
            tilex = x / tilesizeX
            tiley = y / tilesizeY
            v = (tilex << 8) | tiley
            name = prefix + encode(v) + ".png"
            tile.save(name)


def intoFormat():
    # at the end, just gzip the file and it will be good enough

    # number of bytes to save the locations
    loc_size = 8
    mapx = x1 / tilesizeX
    mapy = y1 / tilesizeX

    # where to start save the TOC
    toc_offset = 8

    # where to start saving the tiles
    tile_offset = toc_offset + (mapx * mapy * loc_size)

    fh = open("map.dat", "wb")

    for x in range(x0, x1, tilesizeX):
        for y in range(y0, y1, tilesizeY):
            tile = im.crop((x, y, x + tilesizeX, y + tilesizeY))

            # save as a png
            # write the pixel data to our file

            tmp = StringIO()
            tile.save(tmp, "png", optimize=True)

            fh.seek(tile_offset)    

            fh.write(tmp.getvalue())
            tmp.close()

            tile_offset = fh.tell()

            # write the header
            fh.seek(toc_offset)
            fh.write(pack(">d", tile_offset))

            toc_offset = fh.tell()

    fh.close()

# experimental format
#intoFormat()

intoFiles()

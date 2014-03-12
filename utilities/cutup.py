"""
slice actor resources from sprite sheets into "animation grid" sprite resources suitable for the animation loader.

this is a glue between the seemingly random layouts that you find on the
internet for spritesheets and the lib2d engine.  using this format means less
manual cutting and pasting spritesheet images and less disk use by
consolidating image resources into a single file.

the output will be a collection of "def" files for loading actors and a master
spritesheet that contains all the images for the supplied actors.

uses pil


for each template:
    read the template and calculate the size of the tiles
    create an image for storing the frames of the animation


animations:
    metadata will not be stored in external files
    animation is loaded with a tile size
    each row is a different direction for the animation
    the loader will know this and create a proper avatar for each image
"""

import sys
import os
from collections import defaultdict

from configobj import ConfigObj


try:
    from PIL import Image
except:
    print("cannot import PIL")
    print("PIL must be installed")
    sys.exit()

# make sure there are enough arguments:
if len(sys.argv) < 2:
    print("USAGE:")
    print("cutup.py template")
    print
    sys.exit()


class PilCutter(object):
    def open(self, filename):
        return Image.open(filename)

    def cut(self, image, area):
        return image.crop(area)

    def paste(self, image, destination, location):
        destination.paste(image, location)

    def save(self, image, filename):
        image.save(filename)

class PygameCutter(object):
    # do some other time
    pass


imgHandler = PilCutter()



def makeFolderStructure():
    if not os.path.exists("actors"): os.mkdir("actors")
    if not os.path.exists(os.path.join("actors", name)):
        os.mkdir(os.path.join("actors", name))
    if not os.path.exists("grids"): os.mkdir("grids")
    if not os.path.exists(os.path.join("actors", name, "animations")):
        os.mkdir(os.path.join("actors", name, "animations"))


def sortTemplates(filenames):
    """
    read the template and determine the size of the tiles
    """

    sizePool = defaultdict(list)

    for fn in filenames:
        config  = ConfigObj(fn)
        section = config['template']
        dim     = section['dimension']

        sizePool[dim].append(filename)

    return sizePool


def parseTemplate(filename):
    xoffset = 0
    yoffset = 0

    config = ConfigObj(filename)
    name = filename[:-9]

    general = config["general"]
    template = config["template"]


    for section,items in config.items():
        if section == "general" or section == "template":
            continue

        # load our default values first, then the values for this section
        d = {}
        d.update(general)
        d.update(items)

        # this will be our new sheet
        frames     = len(d["direction0"].split())
        directions = [ i for i in d.keys() if i[:9] == "direction" ]
        directions.sort() 

        # could be a much better way of doing this, i am sure
        misc = {}
        for key in [ i for i in items.keys() if i[:9] != "direction" ]:
            misc[key] = items[key]

        # this will be our new config
        defn = ConfigObj()
        defn.filename = os.path.join("actors", name, "animations", section + ".ini")
        defn["general"] = {}
        defn["general"]["layout"] = "animation grid"
        defn["general"]["image"] = name + "-" + section + ".png"
        defn["general"]["dimension"] = template["dimension"]
        defn["general"]["transparency"] = template["transparency"]
        defn["general"]["directions"] = len(directions)
        defn["general"]["frames"] = frames
        defn["general"]["loop forever"] = template["loop forever"]
        defn["general"].update(general)

        for i in range(frames):
            defn["frame" + str(i)] = misc

        # open up our spritesheet and do some surgery        
        sheet = imgHandler.open(template['image'])

        tilex, tiley = template["dimension"]
        tilex = int(tilex)
        tiley = int(tiley)
        out = Image.new("RGB",  (tilex * frames, tiley * len(directions)))

        # build the sheets from the "directionX" keywords
        for k in directions:
            i = int(k[9:])
            row = i * tiley
            tiles = d[k]
            tiles.strip()
            tiles = tiles.split()
            for t in range(len(tiles)):
                tile = tiles[t].split(",")
                tile = (int(tile[0]) * tilex, int(tile[1]) * tiley)
                image = sheet.crop((tile[0], tile[1], tile[0] + tilex, tile[1] + tiley))
                out.paste(image, (t * tilex, row))

        # save the image
        out.save(os.path.join("grids",name + "-" + section + ".png"))

        # save the config
        defn.write()


pool = sortTemplates(sys.argv[1:])

for size, filename in pool.items():
    readTemplate(filename)


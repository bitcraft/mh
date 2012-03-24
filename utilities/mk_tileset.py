"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
As much as Tile's "Object Layers" are useful, they sometimes just don't work
well enough.  For simple doors, npc spawner locations, etc, they don't snap
well and the interface is a little jenky.  not to mention, there is no
spreadsheet-like view that would make wide changes easy to do.

to get around this limitation, the script will generate a tileset that is
suitable to be used in place of object layers.

tested against tiled qt 0.7.1.

uses pygame

--bitcraft
leif.theden at gmail.com
"""

from xml.dom.minidom import Document
import os.path
import pygame


# tile size
tilesize = (16, 16)

# size in tiles
imagesize = (16, 16)

# colors of the image, also of the titles
image_fg = (0,0,0)
image_bg = (240,240,240)

# for each colorset, there will be a set of numbered tiles
colorsets = []

# white on blue
colorsets.append(("NPC", (255,255,255), (20,0,180)))

# white on red
colorsets.append(("DOOR", (255,255,255), (180,10,20)))

# white on green
colorsets.append(("ITEM", (255,255,255), (0,120,10)))

# black on light-blue
colorsets.append(("", (0,0,0), (200,200,255)))

# black on light-pink
colorsets.append(("", (0,0,0), (255,200,200)))

# black on light-green
colorsets.append(("", (0,0,0), (200,255,200)))

# black on light-grey
colorsets.append(("", (0,0,0), (200,200,200)))

# file name of the image
path = "../resources/tilesets/"
filename = "controlset"


pygame.font.init()

font = pygame.font.Font("../resources/fonts/visitor1.ttf", 10)
image = pygame.Surface((tilesize[0] * imagesize[0], (tilesize[1] * (imagesize[1] + 1)) * len(colorsets)))
image.fill(image_bg)

# create a new xml document for our tiled tileset
doc = Document()

tileset = doc.createElement("tileset")
tileset.setAttribute("name", "control")
tileset.setAttribute("tilewidth", str(imagesize[0]))
tileset.setAttribute("tileheight", str(imagesize[1]))
doc.appendChild(tileset)

rect = image.get_rect()
imageE = doc.createElement("image")
imageE.setAttribute("source", filename + ".png")
imageE.setAttribute("width", str(rect.width))
imageE.setAttribute("height", str(rect.height))
tileset.appendChild(imageE)

yoffset = 0
gid = 0
guid = 1 

for title, fg, bg in colorsets:
    gid += 16

    # display the title inside the tileset
    title = title[:16].lower()
    xoffset = (8 - len(title) / 2) * tilesize[0]
    for x in xrange(0, len(title)):
        txt = font.render(title[x], 1, image_fg, image_bg)
        image.blit(txt, (xoffset + 2, yoffset + 3))
        xoffset += imagesize[0]   

    yoffset += imagesize[1]

    image.fill(bg,(0,yoffset,imagesize[0]*tilesize[0],imagesize[1]*tilesize[1]))

    # add the tiles to the image and the xml document
    local_id = 0
    for y in xrange(0, imagesize[1]):
        for x in xrange(0, imagesize[0]):

            # blit the hex id on the image
            txt = font.render(hex(local_id)[2:].upper(), 0, fg, bg)
            image.blit(txt,(x*tilesize[0]+2,y*tilesize[1]+yoffset+3))

            # make the xml elements for the tile
            tile = doc.createElement("tile")

            # this is the gid for the tile
            tile.setAttribute("id", str(gid))
            tileset.appendChild(tile)

            # tiled supports metadata for tiles using element "properties"
            props = doc.createElement("properties")
            tile.appendChild(props)

            # name of the group this tile belongs to
            prop = doc.createElement("property")
            prop.setAttribute("name", "group")
            prop.setAttribute("value", title)
            props.appendChild(prop)

            # number displayed on the tile, not related to gid
            prop = doc.createElement("property")
            prop.setAttribute("name", "value")
            prop.setAttribute("value", str(local_id))
            props.appendChild(prop)

            # guid of the tile, not related to gid
            prop = doc.createElement("property")
            prop.setAttribute("name", "guid")
            prop.setAttribute("value", str(guid))
            props.appendChild(prop)

            gid += 1
            local_id += 1
            guid += 1

    yoffset += (imagesize[1] * tilesize[1])

# write the image file
pygame.image.save(image, os.path.join(path, filename + ".png"))

# write the xml document (.tsx)
with open(os.path.join(path, filename + ".tsx"), "w") as fh:
    fh.write(doc.toprettyxml(indent=" "))

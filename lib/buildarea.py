from lib2d.server.area import AdventureArea
from lib2d.common.bbox import BBox
from lib2d.common import res
from pytmx import tmxloader



def fromTMX(parent, mapname):
    """Create a new area from a tmx map

    This body (called parent) must already be connected to the data tree,
    otherwise body loading will not work and area building will fail.
    """


    def toWorld(data, (x, y, l)):
        """ translate tiled map coordinates to world coordinates """
        return y*data.tileheight, x*data.tilewidth, l


    area = AdventureArea()
    parent.add(area)
    area.setParent(parent)
    area.mappath = res.mapPath(mapname)
    data = tmxloader.load_tmx(area.mappath)


    # set the boundries (extent) of this map
    area.setExtent(((0,0), \
        (data.height * data.tileheight, data.width * data.tilewidth)))

    props = data.getTilePropertiesByLayer(-1)


    # load the level geometry and set it 
    rects = []
    for rect in tmxloader.buildDistributionRects(data, "Control", real_gid=1):
        # translate the tiled coordinates to world coordinates
        x, y, sx, sy = rect
        rects.append(Rect(y,x,sy,sx))
    area.setLayerGeometry(4, rects)


    # load the npc's and place them in the default positions 
    npcs = [ p for p in props if p[1].get('group', None) == 'npc' ] 

    for (gid, prop) in npcs:
        pos = data.getTileLocation(gid)
        if len(pos) > 1:
            msg = "control gid: {} is used in more than one locaton"
            raise Exception, msg.format(gid)

        x, y, z = toWorld(data, pos[0])
        x += data.tileheight     # needed to position bodies correctly
        y += data.tilewidth / 2  # needed to position bodies correctly
        body = area._parent.getChildByGUID(int(prop['guid']))

        area.add(body)
        d, w, h = (8, 10, 8)
        z = 4
        bbox = BBox(x-d, y, z, d, w, h)
        area.setBBox(body, bbox)
        area.setOrientation(body, "south")


    # load the items and place them where they should go
    # items can have duplicate entries
    items = [ p for p in props if p[1].get('group', None) == 'item' ]
    done = [] 

    for (gid, prop) in items:
        if gid in done: continue
        done.append(gid)

        locations = data.getTileLocation(gid)
        body = area._parent.getChildByGUID(int(prop['guid']))
        copy = False

        for x, y, l in locations:
            x, y, z = toWorld(data, (x, y, l))
            w, h, d = (10, 6, 8)
            z = 0

            x += data.tileheight - d / 2   # needed to position bodies correctly
            y += data.tilewidth / 2 - w / 2  # needed to position bodies correctly

            bbox = BBox(x-d, y, z, d, w, h)

            # bodies cannot exists in multiple locations, so a copy is
            # made for each
            if copy:
                body = body.copy()

            area.add(body)
            area.setBBox(body, bbox)
            area.setOrientation(body, "south")
            copy = True 


    # handle the exits
    # here only the exits and positions are saved
    # another class will have to finalize the exits by adding a ref to
    # guid of the other area
    exits = [ p for p in props if p[1].get('group', None) == 'door' ]
    for gid, prop in exits:
        x, y, l = toWorld(data, data.getTileLocation(gid)[0])
        area.exits[prop['guid']] = ((x, y, l), None)

    return area


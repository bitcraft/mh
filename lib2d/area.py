import res
from pathfinding.astar import Node
from objects import GameObject
from pygame import Rect
from pathfinding import astar
from lib2d.signals import *
from lib2d.objects import AvatarObject
from lib2d.zone import Zone
import math

import pymunk

cardinalDirs = {"north": math.pi*1.5, "east": 0.0, "south": math.pi/2, "west": math.pi}



class PathfindingSentinel(object):
    """
    this object watches a body move and will adjust the movement as needed
    used to move a body when a path is set for it to move towards
    """

    def __init__(self, body, path):
        self.body = body
        self.path = path
        self.dx = 0
        self.dy = 0

    def update(self, time):
        if worldToTile(bbox.origin) == self.path[-1]:
            pos = path.pop()
            theta = math.atan2(self.destination[1], self.destination[0])
            self.destination = self.position + self.destination
            self.dx = self.speed * cos(theta)
            self.dy = self.speed * sin(theta) 

        self.area.movePosition(self.body, (seldf.dx, self.dy, 0))


class AbstractArea(GameObject):
    pass


class Sound(object):
    """
    Class that manages how sounds are played and emitted from the area
    """

    def __init__(self, filename, ttl):
        self.filename = filename
        self.ttl = ttl
        self._done = 0
        self.timer = 0

    def update(self, time):
        if self.timer >= self.ttl:
            self._done = 1
        else:
            self.timer += time

    @property
    def done(self):
        return self._done



class AdventureMixin(object):
    """
    Mixin class that contains methods to translate world coordinates to screen
    or surface coordinates.
    The methods will translate coordinates of the tiled map

    TODO: manipulate the tmx loader to swap the axis
    """

    def tileToWorld(self, (x, y, z)):
        xx = int(x) * self.tmxdata.tileheight
        yy = int(y) * self.tmxdata.tilewidth
        return xx, yy, z


    def pixelToWorld(self, (x, y)):
        return Vec3d(y, x, 0)


    def toRect(self, bbox):
        # return a rect that represents the object on the xy plane
        # currently this is used for geometry collision detection
        return Rect((bbox.x, bbox.y, bbox.depth, bbox.width))


    def worldToPixel(self, (x, y, z)):
        return Vec2d((y, x))


    def worldToTile(self, (x, y, z)):
        xx = int(x) / self.tmxdata.tilewidth
        yy = int(y) / self.tmxdata.tileheight
        zz = 0
        return xx, yy, zz


    def setForce(self, body, (x, y, z)):
        body.acc = Vec2d(x, y)


class PlatformMixin(object):
    """
    Mixin class is suitable for platformer games
    """

    def defaultPosition(self):
        return 0,0


    def translate(self, (x, y, z)):
        return y, z


    def toRect(self, bbox):
        # return a rect that represents the object on the zy plane
        return Rect((bbox.y, bbox.z+bbox.height, bbox.width, bbox.height))


    """
    the underlying physics 'engine' is only capable of calculating 2 axises.
    for playformer type games, we use the zy plane for calculations
    """

    def grounded(self, body):
        try:
            return self._grounded[body]
        except:
            return False


    def applyForce(self, body, (x, y, z)):
        body.acc += Vec2d(y, z)


    def worldToPixel(self, (x, y)):
        return (x*self.scaling, y*self.scaling)


    def worldToTile(self, (x, y, z)):
        xx = int(x) / self.tmxdata.tilewidth
        yy = int(y) / self.tmxdata.tileheight
        zz = 0
        return xx, yy, zz


"""
    G R O U P S


    1:  LEVEL GEOMETRY
    2:  ZONES



    T Y P E S

    1:  THE PLAYER (AS SET BY THE LEVEL STATE)
    2:  ZONES

"""

class PlatformArea(AbstractArea, PlatformMixin):
    """
    2D environment for things to live in.
    Includes basic pathfinding, collision detection, among other things.

    Physics simulation is handled by pymunk/chipmunk 2d physics.

    Bodies can exits in layers, just like maps.  since the y values can
    vary, when testing for collisions the y value will be truncated and tested
    against the quadtree that is closest.  if there is no quadtree, no
    collision testing will be done.

    There are a few hacks to be aware of:
        bodies move in 3d space, but level geometry is 2d space
        when using pygame rects, the y value maps to the z value in the area

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    Expects to load a specially formatted TMX map created with Tiled.
    Layers:
        Control Tiles
        Upper Partial Tiles
        Lower Partial Tiles
        Lower Full Tiles

    Contains a very basic discrete collision system.

    The control layer is where objects and boundries are placed.  It will not
    be rendered.  Your map must not have any spaces that are open.  Each space
    must have a tile in it.  Blank spaces will not be rendered properly and
    will leave annoying trails on the screen.

    The control layer must be created with the utility included with lib2d.  It
    contains metadata that lib2d can use to layout and position objects
    correctly.

    REWRITE: FUNCTIONS HERE SHOULD NOT CHANGE STATE

    Handle mapping of physics bodies to game entities


    NOTE: some of the code is specific for maps from the tmxloader
    """

    gravity = (0, 50)


    def defaultSize(self):
        # TODO: this cannot be hardcoded!
        return (10, 8)


    def __init__(self):
        AbstractArea.__init__(self)
        self.subscribers = []

        self.exits    = {}
        self.messages = []
        self.tmxdata = None
        self.mappath = None
        self.sounds = []
        self.soundFiles = []
        self.inUpdate = False
        self.drawables = []         # HAAAAKCCCCKCK
        self.changedAvatars = True  #hack
        self.time = 0
        self.music_pos = 0
        self._addQueue = []
        self._removeQueue = []
        self._addQueue = []

        self.flashes = []
        self.inUpdate = False
        self._removeQueue = []

        # temporary storage of physics stuff
        self.temp_positions = {}

        # internal physics stuff
        self.geometry = {}
        self.shapes = {}
        self.bodies = {}
        self.physicsgroup = None
        self.extent = None          # absolute boundaries of the area
        self.scaling = 1.0          # MUST BE FLOAT 


    def load(self):
        def toChipPoly(rect):
            return (rect.topleft, rect.topright,
                    rect.bottomright, rect.bottomleft)


        import pytmx

        self.tmxdata = pytmx.tmxloader.load_pygame(
                       self.mappath, force_colorkey=(128,128,0))

        # get sounds from tiles
        for i, layer in enumerate(self.tmxdata.tilelayers):
            props = self.tmxdata.getTilePropertiesByLayer(i)
            for gid, tileProp in props:
                for key, value in tileProp.items():
                    if key[4:].lower() == "sound":
                        self.soundFiles.append(value)

        # get sounds from objects
        for i in [ i for i in self.getChildren() if i.sounds ]:
            self.soundFiles.extend(i.sounds)

        self.space = pymunk.Space()
        self.space.gravity = self.gravity

        # transform the saved geometry into chipmunk geometry and add it
        # bug: will not work with multiple layers
        geometry = []
        for layer, rects in self.geometry.items():
            for rect in rects:
                shape = pymunk.Poly(self.space.static_body, toChipPoly(rect))
                shape.friction = 1.0
                shape.group = 1
                #shape.layers = layer
                geometry.append(shape)

        self.space.add(geometry)

        # dont worry about setting the player group, that will be set by the
        # levelstate
        self.groups = 2

        # just assume we have the correct types under us
        for child in self._children:
            if isinstance(child, AvatarObject):
                if child.physics:
                    body = pymunk.Body(5, pymunk.inf)
                    body.position = self.temp_positions[child]
                    body.friction = 1.0
                    shape = pymunk.Poly.create_box(body, size=child.size[:2])
                    self.bodies[child] = body
                    self.shapes[child] = shape
                    self.space.add(body, shape)

                else:
                    rect = Rect(self.temp_positions[child], child.size[:2])
                    shape = pymunk.Poly(self.space.static_body, toChipPoly(rect))
                    shape.friction = 1.0
                    self.shapes[child] = shape
                    self.space.add(shape)

            elif isinstance(child, Zone):
                points = toChipPoly(child.extent)
                shape = pymunk.Poly(self.space.static_body, points)
                shape.collision_type = 2
                self.shapes[child] = shape
                self.space.add(shape)


    def unload(self):
        self.bodies = {}
        self.shapes = {}
        self.physicsgroup = None
        self.space = None


    def add(self, child, pos=None):
        AbstractArea.add(self, child)

        # don't do anything with the physics engine here
        # handle it in load(), where the area is prepped for use

        if isinstance(child, AvatarObject):
            if pos is None:
                pos = self.defaultPosition()
            else:
                pos = self.translate(pos)

            self.temp_positions[child] = pos
            self.changedAvatars = True


    def remove(self, entity):
        if self.inUpdate:
            self._removeQueue.append(entity)
            return

        AbstractArea.remove(self, entity)
        del self.bodies[entity]
        self.changedAvatars = True

        # hack
        try:
            self.drawables.remove(entity)
        except (ValueError, IndexError):
            pass


    def getBody(self, entity):
        return self.bodies[entity]


    def setLayerGeometry(self, layer, rects):
        """
        set the layer's geometry.  expects a list of rects.
        """

        self.geometry[layer] = rects


    def pathfind(self, start, destination):
        """Pathfinding for the world.  Destinations are 'snapped' to tiles.
        """

        def NodeFactory(pos):
            x, y = pos[:2]
            l = 0
            return Node((x, y))

            try:
                if self.tmxdata.getTileGID(x, y, l) == 0:
                    node = Node((x, y))
                else:
                    return None
            except:
                return None
            else:
                return node

        start = self.worldToTile(start)
        destination = self.worldToTile(destination)
        path = astar.search(start, destination, NodeFactory)
        return path


    def emitText(self, text, pos=None, entity=None):
        if pos==entity==None:
            raise ValueError, "emitText requires a position or entity"

        if entity:
            pos = self.bodies[entity].bbox.center
        emitText.send(sender=self, text=text, position=pos)
        self.messages.append(text)


    def emitSound(self, filename, pos=None, entity=None, ttl=350):
        if pos==entity==None:
            raise ValueError, "emitSound requires a position or entity"

        self.sounds = [ s for s in self.sounds if not s.done ]
        if filename not in [ s.filename for s in self.sounds ]:
            self.sounds.append(Sound(filename, ttl))
            if entity:
                pos = self.bodies[entity].position
            for sub in self.subscribers:
                sub.emitSound(filename, pos)


    def update(self, time):
        self.inUpdate = True
        self.time += time

        [ sound.update(time) for sound in self.sounds ]

        for entity, body in self.bodies.items():
            grounding = {
                'normal' : pymunk.Vec2d.zero(),
                'penetration' : pymunk.Vec2d.zero(),
                'impulse' : pymunk.Vec2d.zero(),
                'position' : pymunk.Vec2d.zero(),
                'body' : None
            }
                    
            def f(arbiter):
                n = -arbiter.contacts[0].normal
                if n.y > grounding['normal'].y:
                    grounding['normal'] = n
                    grounding['penetration'] = -arbiter.contacts[0].distance
                    grounding['body'] = arbiter.shapes[1].body
                    grounding['impulse'] = arbiter.total_impulse
                    grounding['position'] = arbiter.contacts[0].position
            body.each_arbiter(f)
            entity.avatar.update(time)

            if grounding['body'] != None:
                friction = -(body.velocity.y/0.05)/self.space.gravity.y

            if grounding['body'] != None and abs(grounding['normal'].x/grounding['normal'].y) < friction:
                entity.grounded = True
            else:
                entity.grounded = False

            if entity.time_update:
                entity.update(time)

        self.space.step(1.0/60)

        # awkward looping allowing objects to be added/removed during update
        self.inUpdate = False
        [ self.add(entity) for entity in self._addQueue ] 
        self._addQueue = []
        [ self.remove(entity) for entity in self._removeQueue ] 
        self._removeQueue = []


    def _sendBodyMove(self, body, caller, force=None):
        position = body.bbox.origin
        bodyAbsMove.send(sender=self, body=body, position=position, caller=caller, force=force)

    
    #  CLIENT API  --------------


    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)


    def getSize(self, entity):
        """ Return 3d size of the object """
        return self.bodies[entity].bbox.size


    def getBody(self, entity):
        return self.bodies[entity]

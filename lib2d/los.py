"""
Start by setting every sightmask and every blindmask to all-0's. 
Set the 'status' variable of every cell to 'generator'.  

Repeat

   For all cells whose status is 'generator', 

      generate a Field of view using the current sightmasks 
      generate a Field of View using a standard FOV algorithm. 
      If they match, set the status to 'perfect'.
      Otherwise count the number of cells difference. 

   End for.

   Pick the 'generator' cell from the above set whose difference is 
       largest.

   Use that cell as a generator to generate a View Area. (Algorithm below)

   If there is a zero bit in the blindmasks of all the cells in the view 
   area, then
       Set the corresponding bit in the sightmasks of all the cells in the 
       View Area.

       Set the corresponding bit in the blindmasks of all the cells within 
       sight radius of any cell in the View Area.
   Otherwise
       Set the 'status' of that cell to 'imperfect.'

Initialize the "included" set to include (only) the seed cell.

Perform an Extended Field-of-View Calculation for the seed cell 
and use the result as the "candidate" list.

Perform a Field-of-View Calculation for the seed cell using 
FastLOS (limited to sight radius) and any bits already assigned.  
The set of cells in the Candidate list which are NOT in this 
list is the "priority" list.

Repeat

   If there are any "Priority" cells left:

      For each "Priority" cell, find the sum of its distances from all 
          the currently "Included" cells.  

      Add the highest-scored (most distant) "Priority" to the "Included"
         list and remove it from the "candidate" and "Priority" lists.  
   else 

      For each "Candidate" cell, find the sum of its distances from all
          the currently "Included" cells.

      Add the highest-scored (most distant) "Candidate" to the "Included"
          list and remove it from the "Candidate" list.   

    End If

   Find the set of cells that is the Field of View for the new cell.

   Set the Candidate list to be set of cells that are members of both
       the current Candidate List and the new cell's FOV.

   Set the Priority list to be the set of cells that are members of both
       the current Priority List and the new cell's FOV. 

Until the Candidate List is empty.

The "included" list now contains all the cells in the generated View Area.
"""

"""
basically, this function appends data to each cell in a 2d map that is used
to quickly calculate LOS on the map.  the burden of LOS is done before the
map is used, and the calculations are not needed during runtime.
"""

from lib2d.fov import BergstromFOV
import math



GENERATOR = 0
PERFECT   = 1
IMPERFECT = 2


def hasZero(x):
    # return True if bit value has a zero in it
    pass


def dist(a, b):
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1]**2))


def circle(a, radius):
    radius = int(radius) / 2
    p = product(xrange(x - radius, x + radius), xrange(y - radius, y + radius))
    return ( pos for pos in p if dist(a, pos) <= rad )


class FastLOS(object):
    """
    FastLOS trades time for memory use to create a fast line of sight function.
    Instance the object, then generate the masks using a known FOV algorithm.
    """

    def __init__(self, data):
        self.data = data
        self._createMasks()


    def calcFOV(self, (x, y), radius):
        cells = circle((x, y), radius)
        origin = self.sightmask[y][x]
        return [ (x, y) for x,y in cells if self.sightmask[y][x] and origin ]


    def generateMasks(self, fov, radius):
        """
        Generate the mask values needed for the FastLOS algorithm

        supply a function that will do accurate checking of FOV.
        """

        height = len(self.data)
        width = len(self.data[0])

        p = product(xrange(height), xrange(width))
        generators=( p for p in status if status[p[0]][p[1]] == GENERATOR )

        while generators:
            maxScore = 0
            maxCell = None

            for cell in generators:
                estimate = set(self.calcFOV(cell, radius))
                visible  = set(fov(cell, radius))

                if visible == estimate:
                    self.status[cell[0]][cell[1]] = PERFECT
                else:
                    score = abs(len(visible) - len(estimate))
                    if score > maxScore:
                        maxScore = score
                        maxCell = cell
            
            viewarea = genViewArea(maxCell, fov, radius)
            zeros = [ hasZero(cell) for cell in viewarea ]

            if all(zeros):
                # set bit is sightmasks
                # set bit in blindmasks
            else:
                self.status[maxCell[0]][maxCell[1]] = IMPERFECT

            p = product(xrange(height), xrange(width))
            generators=( p for p in status if status[p[0]][p[1]] == GENERATOR )

        self.init = True


    def _createMasks(self):
        height = len(self.data)
        width = len(self.data[0])

        self.sightmask = []
        self.blindmask = []
        self.status = []
        for y in xrange(height):
            self.sightmask.append(array.array('d', [0] * width))
            self.blinkmask.append(array.array('d', [0] * width))
            self.status.append(array.array('b', [GENERATOR] * width))
        self.init = False


    def _longFOV(self, (x, y)):
        """
        Return all the cells that are in sight of (x, y), without a radius
        limit
        """

        pass


    def _genViewArea(self, seed, fov, radius, ext=200):
        included = [seed]

        candidates = set(fov(seed, ext))
        priority = candidates - set(self.calcFOV(seed, radius))

        while candidates:
            if priority:
                maxScore = 0
                maxCell = None
                for cell in priority:
                    score = sum(dist(cell, other) for other in included)
                    if score > maxScore:
                        maxScore = score
                        maxCell = cell

                included.append(maxCell)
                candidate.remove(maxCell)
                priority.remove(maxCell)

            else:
                maxScore = 0
                maxCell = None
                for cell in priority:
                    score = sum(dist(cell, other) for other in included)
                    if score > maxScore:
                        maxScore = score
                        maxCell = cell

                included.append(maxCell)
                candidates.remove(maxCell)

            visible = set(fov(maxCell, radius))
            candidates |= visible
            priority   |= visible

        return included



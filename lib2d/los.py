"""
Start by setting every sightmask and every blindmask to all-0's. 
Set the 'status' variable of every tile to 'generator'.  

Repeat

   For all tiles whose status is 'generator', 

      generate a Field of view using the current sightmasks 
      generate a Field of View using a standard FOV algorithm. 
      If they match, set the status to 'perfect'.
      Otherwise count the number of tiles difference. 

   End for.

   Pick the 'generator' tile from the above set whose difference is 
       largest.

   Use that tile as a generator to generate a View Area. (Algorithm below)

   If there is a zero bit in the blindmasks of all the cells in the view 
   area, then
       Set the corresponding bit in the sightmasks of all the cells in the 
       View Area.

       Set the corresponding bit in the blindmasks of all the cells within 
       sight radius of any cell in the View Area.
   Otherwise
       Set the 'status' of that tile to 'imperfect.'

Initialize the "included" set to include (only) the seed tile.

Perform an Extended Field-of-View Calculation for the seed tile 
and use the result as the "candidate" list.

Perform a Field-of-View Calculation for the seed tile using 
FastLOS (limited to sight radius) and any bits already assigned.  
The set of tiles in the Candidate list which are NOT in this 
list is the "priority" list.

Repeat

   If there are any "Priority" cells left:

      For each "Priority" tile, find the sum of its distances from all 
          the currently "Included" tiles.  

      Add the highest-scored (most distant) "Priority" to the "Included"
         list and remove it from the "candidate" and "Priority" lists.  
   else 

      For each "Candidate" tile, find the sum of its distances from all
          the currently "Included" tiles.

      Add the highest-scored (most distant) "Candidate" to the "Included"
          list and remove it from the "Candidate" list.   

    End If

   Find the set of tiles that is the Field of View for the new tile.

   Set the Candidate list to be set of tiles that are members of both
       the current Candidate List and the new tile's FOV.

   Set the Priority list to be the set of tiles that are members of both
       the current Priority List and the new tile's FOV. 

Until the Candidate List is empty.

The "included" list now contains all the tiles in the generated View Area.


"""

# need two 2d arrays that are 64bit integers, init to 0

def hasZero(x):
    # return True if bit value has a zero in it
    pass


def preprocess():
    imperfect = []
    perfect = []
    heap = []


    while generators:

        for tile in generators:
            visible = set(fov(tile))
            estimate = set(fastlos(tile))

            if visible == estimate:
                perfect.append(tile)
            else:
                score = abs(len(visible) - len(estimate))
                heap.push((score, tile))
       
        tile = heap.pop()
        viewarea = genViewArea(tile)

        zeros = [ hasZero(tile) for tile in viewarea ]
        if all(zeros):
            # set bit is sightmasks
            # set bit in blindmasks
        else:
            imperfect.append(g)

    return



def genViewArea(seed):
    included = [seed]

    candidates = set(fov(seed))
    priority = candidates - set(fastlos(seed))

    while candidates:
        if priority:
            highest = None
            maxScore = 0
            for tile in priority:
                score = sum(dist(tile, other) for other in included)
                if score > maxScore: highest = tile

            included.append(highest)
            candidate.remove(highest)
            priority.remove(highest)

        else:
            highest = None
            maxScore = 0
            for tile in priority:
                score = sum(dist(tile, other) for other in included)
                if score > maxScore: highest = tile

            included.append(highest)
            candidates.remove(highest)

        visible = set(fov(highest))
        candidates |= visible
        priority |= visible

        
    return included


def fov_full(data, tile):
    # do fov without a radius limit

def fov(data, tile):
    # return a real fov for this tile and area

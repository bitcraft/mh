this is a ongoing project for some sort of adventure game.

python/pygame adventure game library
    native support for tiled maps
    supports keyboard and joystick movement
    save game and persistence for all objects
    scrolling map
    animated sprites


started during pyweek sept '11, has slowly morphed into something else.


people interested in the game are more than welcome to fork the game and try
to make something of it.  i develop the game and library, lib2d, in my spare
time and sometimes will make huge changes.  that being said, there isn't much
documentation except for the comments.

the game uses a pickle to save the game.  if you make changes to any class that
exists in the pickle (area, avatarobject, ...), then you will have to rebuild
the game pickle.  just run "buildworld.py".  this is also the script that
generates the starting world.

the guid's set in the pickle match the guid's stored in control.tsx found in
tilesets.



RUNNING:

after you download mh, you will need to initialize the world pickle.  simply
run 'buildworld.sh'.  this will create two files for the pickle, then you can
run 'run.py' to get going.

run.py contains a few game modes that you can try.  simply uncomment the mode
to try in the section near the bottom of the file.

HAVE FUN!

Lib2d is a game engine that I have been developing to create PyWeek games.


----- this is an experimental version for adventure games -----

What it does:
    State (context) management
    Animated Sprites with multiple animations and automatic flipping
    TMX level importing
    Integrated Tiled Editing
    Fast, efficient tilemap rendering with parallax support
    Basic GUI features
    Integrated Chipmunk dynamics (pymunk)
    Advanced AI (pygoap)
    Integrated animation and input handling (fsa.py)
    Simplified save game support
    Dialogs


Game Structure Overview:
    Map is designed in Tiled with special layer (controlset.tsx)
    Game objects are created in world.py and assigned GUID control numbers
    The 'world' data structure is pickleable and becomes the save game
    When engine is started, the world data structure can be used to play


Control:
    Lib2d wraps all pygame events for player input so they can be remapped.
    It also make keyboard and joystick controls interchangeable at runtime.
    Using fsa.py, instead of coding the behavour of the controls, you can
        use a finite state machine to define how the character changes states.

Tilemap:
    The tilemap uses a special surface that gets updated in the background
    (or by another thread).  It performs very well when scrolling.  Large TMX
    maps can be used since only the visible portions of the map are rendered.


Physics:
    The library uses pymunk and cannot work without it.  The obvious benefits
    are a fast physics system (not more colliding rects!) and it has good
    integration with the TMX loader.

    You can define your walls in tiles, and they will get loaded into the
    Chipmunk engine automatically.

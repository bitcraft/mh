class GameState(object):
    """
    Game states are a logical way to break up distinct portions
    of a game.
    """

    def __init__(self):
        """
        Called when objest is instanced.

        Not a good idea to load large objects here since it is possible
        that the state is simply instanced and placed in a queue.

        Ideally, any initialization will be handled in activate() since
        that is the point when assets will be required.
        """        


        self.activated = False


    def activate(self):
        """
        Called when focus is given to the state for the first time

        *** When overriding this method, set activated to true ***
        """

        pass


    def reactivate(self):
        """
        Called with focus is given to the state again
        """

        pass


    def deactivate(self):
        """
        Called when focus is being lost
        """

        pass


    def terminate(self):
        """
        Called when the state is no longer needed
        The state will be lost after this is called
        """

        pass


    def draw(self, surface):
        """
        Called when state can draw to the screen
        """

        pass


    def handle_event(self, event):
        """
        Called when there is an pygame event to process

        Better to use handle_command() or handle_commandlist()
        for player input
        """

        pass


    def update(self, time):
        """
        Called when state has a chance to process logic

        Time is milliseconds passed since last update
        """

        pass


    def handle_command(self, command):
        """
        Called when there is an input command to process
        """
 
        pass


    def handle_commandlist(self, cmdlist):
        """
        Called when there are multiple input commands to process
        This is more effecient that handling them one at a time
        """

        pass

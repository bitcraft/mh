class PickleError(Exception):
    def __init__(self,errormess):self.errormess = errormess
    def __str__(self):return repr(self.errormess)
    
class ServerError(Exception):
    def __init__(self,errormess):self.errormess = errormess
    def __str__(self):return repr(self.errormess)
    
class SocketError(Exception):
    def __init__(self,errormess):self.errormess = errormess
    def __str__(self):return repr(self.errormess)

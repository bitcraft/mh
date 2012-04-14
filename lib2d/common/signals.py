from dispatch import Signal, receiver

"""
Define signals used in Lib2d here
"""

bodyRelMove = Signal(providing_args=["body", "position", "force"])
bodyAbsMove = Signal(providing_args=["body", "position", "force"])
bodyWarp    = Signal(providing_args=["body", "area"])
emitSound   = Signal(providing_args=["filename", "position"])

timeSignal  = Signal(providing_args=["time"])

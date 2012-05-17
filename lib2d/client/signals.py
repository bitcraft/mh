from lib2d.common.dispatch import Signal, receiver

"""
Define signals used in Lib2d here
"""

# signals used in area.py
bodyRelMove = Signal(providing_args=["body", "position", "force"])
bodyAbsMove = Signal(providing_args=["body", "position", "force"])
bodyWarp    = Signal(providing_args=["body", "area"])
emitSound   = Signal(providing_args=["filename", "position"])

# signals relevant for the engine
timeSignal = Signal(providing_args=["time"])
drawSignal = Signal(providing_args=["surface"])
inputSignal = Signal(providing_args=["driver", "args"])

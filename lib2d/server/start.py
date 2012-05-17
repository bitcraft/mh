"""
Start a local server for single-player games.
The server will be run in a seperate process.
"""

from multiprocessing import Process


def _start_local():
    print "STATING"


def start_local():
    p = Process(target=_start_local)
    p.start()
    p.join()

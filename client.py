#!/usr/bin/env python

"""
Runs the frontend for the lib2d client.
Based on the Tkinter.

not complete.
"""

from Tkinter import *


class AddServerDialog():
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()


class Frontend(object):

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.button_quit = Button(frame, text="Quit")
        self.button_quit.pack()

        self.button_addserver = Button(frame, text="Add Server")
        self.button_addserver.pack()


root = Tk()
app = Frontend(root)

root.mainloop()

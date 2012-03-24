"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

from lib2d import UpdateableObject



class Timer(UpdateableObject):
    def __init__(self, alarm=None):
        self._alarm = alarm
        self.reset()

    def update(self, time):
        self.value += time

    def reset(self):
        self.value = 0.0

    #@property
    def get_alarm(self):
        return self._alarm

    #@alarm.setter
    def set_alarm(self, alarm):
        self._alarm = alarm
        self.value = 0.0

    alarm = property(get_alarm, set_alarm)

    @property
    def finished(self):
        if self.alarm != None:
            return self.value >= self.alarm
        else:
            return True

class CallbackTimer(Timer):
    def __init__(self, alarm=None, callback=None, args=[]):
        super(CallbackTimer, self).__init__(alarm)
        self.callback = (callback, args)

    def update(self, time):
        self.value += time

        if self.finished:
            self.callback[0](*self.callback[1])
            return False

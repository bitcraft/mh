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

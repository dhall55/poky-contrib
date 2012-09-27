from threading import Event, Thread
'''
    Quartz is mainly used for receiving events from bitbake.
    interval: interval time
    function: called function
'''
class Quartz(Thread):

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)

    def cancel(self):
        self.finished.set()
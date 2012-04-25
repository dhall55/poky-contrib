import threading
import time
import logging
class eventTimer(threading.Thread):
        """
        simple timer to poll bitbake commands one by one and handle event object into json data
        """
        def __init__(self, seconds, func, args=()):
            threading.Thread.__init__(self)
            self.runTime = seconds
            self.func = func
            self.args = args
            self.setDaemon(True)

        def run(self):
            while True:
                time.sleep(self.runTime)
                apply(self.func, self.args)

def event_handle_idle_func(*args):
    eventHandler  = args[0]
    eventQueue    = args[1]
    handler      = args[2]
    event = eventHandler.getEvent()
    while event:
        eventValue = handler.handle_event(event)
        if eventValue:
            eventQueue.pushEventIntoQueue(eventValue)
        event = eventHandler.getEvent()
#    return True
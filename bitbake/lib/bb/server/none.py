#
# BitBake 'dummy' Passthrough Server
#
# Copyright (C) 2006 - 2007  Michael 'Mickey' Lauer
# Copyright (C) 2006 - 2008  Richard Purdie
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
    This module implements a passthrough server for BitBake.

    Use register_idle_function() to add a function which the server
    calls from within idle_commands when no requests are pending. Make sure
    that those functions are non-blocking or else you will introduce latency
    in the server's main loop.
"""

import time
import logging
import signal
import bb
import bb.event
logger = logging.getLogger('BitBake')

DEBUG = False

import inspect, select

class BitBakeServerCommands():
    def __init__(self, server):
        self.server = server

    def runCommand(self, command):
        """
        Run a cooker command on the server
        """
        #print "Running Command %s" % command
        return self.cooker.command.runCommand(command)

    def terminateServer(self):
        """
        Trigger the server to quit
        """
        self.server.server_exit()
        #print "Server (cooker) exitting"
        return

    def ping(self):
        """
        Dummy method which can be used to check the server is still alive
        """
        return True

eventQueue = []

from bb.server.process import ProcessEventQueue
from Queue import Empty

class BBUIEventQueue(ProcessEventQueue):
    def __init__(self, BBServer):
        self.BBServer = BBServer
        ProcessEventQueue.__init__(self)

    def waitEvent(self, timeout):
        event = self.getEvent()
        if event:
            return event
        self.BBServer.idle_commands(timeout)
        return self.getEvent()

    def getEvent(self):
        try:
            return self.get(False)
        except Empty:
            self.BBServer.idle_commands(0)
            return None

# Dummy signal handler to ensure we break out of sleep upon SIGCHLD
def chldhandler(signum, stackframe):
    pass

class BitBakeNoneServer():
    # remove this when you're done with debugging
    # allow_reuse_address = True

    def __init__(self):
        self._idlefuns = {}
        self.commands = BitBakeServerCommands(self)
        self.event_queue = BBUIEventQueue(self)
        self.event = bb.server.process.EventAdapter(self.event_queue)

    def addcooker(self, cooker):
        self.cooker = cooker
        self.event_handle = bb.event.register_UIHhandler(self)
        self.commands.cooker = cooker

    def register_idle_function(self, function, data):
        """Register a function to be called while the server is idle"""
        assert hasattr(function, '__call__')
        self._idlefuns[function] = data

    def idle_commands(self, delay):
        #print "Idle queue length %s" % len(self._idlefuns)
        #print "Idle timeout, running idle functions"
        #if len(self._idlefuns) == 0:
        nextsleep = delay
        for function, data in self._idlefuns.items():
            try:
                retval = function(self, data, False)
                #print "Idle function returned %s" % (retval)
                if retval is False:
                    del self._idlefuns[function]
                elif retval is True:
                    nextsleep = None
                elif nextsleep is None:
                    continue
                elif retval < nextsleep:
                    nextsleep = retval
            except SystemExit:
                raise
            except:
                import traceback
                traceback.print_exc()
                self.commands.runCommand(["stateShutdown"])
                pass
        if nextsleep is not None:
            #print "Sleeping for %s (%s)" % (nextsleep, delay)
            signal.signal(signal.SIGCHLD, chldhandler)
            time.sleep(nextsleep)
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)

    def server_exit(self):
        # Tell idle functions we're exiting
        for function, data in self._idlefuns.items():
            try:
                retval = function(self, data, True)
            except:
                pass
        bb.event.unregister_UIHhandler(self.event_handle)

class BitBakeServerConnection():
    def __init__(self, server):
        self.server = server.server
        self.connection = self.server.commands
        self.events = self.server.event_queue
        for event in bb.event.ui_queue:
            self.server.event_queue.put(event)

    def terminate(self):
        try:
            self.connection.terminateServer()
        except:
            pass

class BitBakeServer(object):
    def initServer(self):
        self.server = BitBakeNoneServer()

    def addcooker(self, cooker):
        self.cooker = cooker
        self.server.addcooker(cooker)

    def getServerIdleCB(self):
        return self.server.register_idle_function

    def saveConnectionDetails(self):
        return

    def detach(self, cooker_logfile):
        self.logfile = cooker_logfile

    def establishConnection(self):
        self.connection = BitBakeServerConnection(self)
        logger.addHandler(bb.event.LogHandler())
        return self.connection

    def launchUI(self, uifunc, *args):
        return bb.cooker.server_main(self.cooker, uifunc, *args)


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
Establish a RPC server to make bitbake server and webpy can communicate each other.
"""

import socket, threading, pickle
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class RestRPCServer:
    def __init__(self, handler=None, clientinfo=("localhost", 0)):

        self.eventQueue = []
        self.eventQueueLock = threading.Lock()
        self.eventQueueNotify = threading.Event()

        self.handler = handler
        self.clientinfo = clientinfo

        self.t = threading.Thread()
        self.t.setDaemon(True)
        self.t.run = self.startCallbackHandler
        self.t.start()

    def popEvent(self):
        self.eventQueueLock.acquire()

        if len(self.eventQueue) == 0:
            self.eventQueueLock.release()
            return

        item = self.eventQueue.pop(0)

        if len(self.eventQueue) == 0:
            self.eventQueueNotify.clear()

        self.eventQueueLock.release()
        return item

    def waitEvent(self, delay):
        self.eventQueueNotify.wait(delay)
        return self.getEvent()

    def pushEventIntoQueue(self, event):
        self.eventQueueLock.acquire()
        self.eventQueue.append(event)
        self.eventQueueNotify.set()
        self.eventQueueLock.release()

    def startCallbackHandler(self):

        server = UIXMLRPCServer(self.clientinfo)
        self.host, self.port = server.socket.getsockname()
        server.register_function(self.popEvent)
        server.register_instance(self.handler)

        server.socket.settimeout(1)

        self.server = server
        while not server.quit:
            server.handle_request()
        server.server_close()

class UIXMLRPCServer (SimpleXMLRPCServer):

    def __init__( self, interface ):
        self.quit = False
        SimpleXMLRPCServer.__init__( self,
                                    interface,
                                    requestHandler=SimpleXMLRPCRequestHandler,
                                    logRequests=False, allow_none=True)

    def get_request(self):
        while not self.quit:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(1)
                return (sock, addr)
            except socket.timeout:
                pass
        return (None, None)

    def close_request(self, request):
        if request is None:
            return
        SimpleXMLRPCServer.close_request(self, request)

    def process_request(self, request, client_address):
        if request is None:
            return
        SimpleXMLRPCServer.process_request(self, request, client_address)

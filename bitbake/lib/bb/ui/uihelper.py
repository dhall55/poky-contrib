# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2006 - 2007  Michael 'Mickey' Lauer
# Copyright (C) 2006 - 2007  Richard Purdie
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

import bb.build

class BBUIHelper:
    def __init__(self):
        self.needUpdate = False
        self.running_tasks = {}
        self.failed_tasks = []

    def eventHandler(self, event):
        if isinstance(event, bb.build.TaskStarted):
            self.running_tasks[event.pid] = { 'title' : "%s %s" % (event._package, event._task) }
            self.needUpdate = True
        if isinstance(event, bb.build.TaskSucceeded):
            del self.running_tasks[event.pid]
            self.needUpdate = True
        if isinstance(event, bb.build.TaskFailed):
            del self.running_tasks[event.pid]
            self.failed_tasks.append( { 'title' : "%s %s" % (event._package, event._task)})
            self.needUpdate = True

    def getTasks(self):
        self.needUpdate = False
        return (self.running_tasks, self.failed_tasks)

    def findServerDetails(self):
        import sys
        import optparse
        from bb.server.xmlrpc import BitbakeServerInfo, BitBakeServerConnection
        host = ""
        port = 0
        parser = optparse.OptionParser(
            usage = """%prog -H address -P port""")

        parser.add_option("-H", "--host", help = "Bitbake server's IP address",
                   action = "store", dest = "host", default = None)

        parser.add_option("-P", "--port", help = "Bitbake server's Port number",
                   action = "store", dest = "port", default = None)

        options, args = parser.parse_args(sys.argv)
        for key, val in options.__dict__.items():
            if key == 'host' and val:
                host = val
            elif key == 'port' and val:
                port = int(val)

        if not host or not port:
            parser.print_usage()
            sys.exit(1)

        serverinfo = BitbakeServerInfo(host, port)
        connection = BitBakeServerConnection(serverinfo)

        server = connection.connection
        eventHandler = connection.events

        return server, eventHandler


#!/usr/bin/env python
#
#
# Copyright (C) 2011        Intel Corporation
#
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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    import bb
except RuntimeError as exc:
    sys.exit(str(exc))

import xmlrpclib

from bb.ui.rest.crumbs.restRpcServer import RestRPCServer
from bb.ui.rest.crumbs.eventhandler import Eventhandler
from bb.ui.rest.crumbs.handlerTimer import eventTimer
from bb.ui.rest.crumbs.handlerTimer import event_handle_idle_func
from bb.ui.rest.web.restEnter import app

def main (server = None, eventHandler = None):
    handler = Eventhandler(server)
    eventRPC = RestRPCServer(handler, clientinfo = ('localhost', 9999))
    timer = eventTimer(0.01, event_handle_idle_func, (eventHandler, eventRPC, handler))
    timer.start()

    try:
        app.run()
    except EnvironmentError as ioerror:
        if ioerror.args[0] == 4:
            pass
    finally:
        server.runCommand(["stateStop"])

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(15)
    sys.exit(ret)
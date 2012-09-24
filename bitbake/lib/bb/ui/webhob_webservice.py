#!/usr/bin/env python
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Lv Xiaotong <xiaotongx.lv@intel.com>
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
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import bb
except RuntimeError as exc:
    sys.exit(str(exc))

try:
    from soaplib.wsgi import Application
    from soaplib.service import rpc
    from soaplib.service import DefinitionBase
    from soaplib.serializers.primitive import String, Integer
    from soaplib.serializers.clazz import ClassSerializer, Array
except ImportError as e:
    sys.exit('Error:%s \nInstall soaplib 1.0 firstly.\nsoaplib:repo @https://github.com/soaplib/soaplib/tree/1_0' % str(e))

try:
    import simplejson as json
except ImportError:
    import json

from bb.ui.crumbs.webserviceeventhandler import WSEventHandler

extraCaches = ['bb.cache_extra:HobRecipeInfo']

class Param(ClassSerializer):
    '''
    this class defined a Webservice params structure for runCommand() method.
    If a client to call runCommand() method, the following is param format:
    param = {
        'function'   = 'string'
        'param_type' = ['string','list','bool','function']
        'params'     = ['str','str1 str2 str3...','true or false' ,'func_name|def func_name()...']
    }
    '''

    __namespace__ = "param"
    function = String
    param_type = Array(String)
    params = Array(String)

func_name = ""
func_body = ""

class WebServiceWrap(DefinitionBase):
    server = None
    eventHandler = None

    @rpc(Param, _returns=String)
    def runCommand(self, param):
        command = []
        function = param.function
        param_type = param.param_type
        params = param.params

        if function:
            command.append(function)
        else:
            return "Error: key(function) value cannot be required."

        if param_type and params:
            if len(param_type) == len(params):
                for item in param_type:
                    if item == 'string':
                        command.append(params.pop(0))
                    elif item == 'bool':
                        command.append(bool(params.pop(0)))
                    elif item == 'list':
                       command.append(params.pop(0).split())
                    else:
                       return "Error: only 'string', 'bool', 'list' should be in param_type"
            else:
                return "Error: key(param_type) value length should be equal to params"
        ret = WebServiceWrap.server.runCommand(command)
        return json.dumps(ret)

    @rpc(_returns=String)
    def getEvent(self):
        event_queue = []
        eventobj = WebServiceWrap.eventHandler.getEvent()
        handler = WSEventHandler()
        while eventobj:
            event = handler.handle_event(eventobj)
            if event:
                event_queue.append(event)
            eventobj = WebServiceWrap.eventHandler.getEvent()
        ret = event_queue if event_queue else None
        return json.dumps({'events':ret})
    
    @rpc(String, String, String, _returns=String)
    def get_images(self, image_name, curr_mach, image_types):
        supported_image_types= {
                "jffs2"         : ["jffs2"],
                "sum.jffs2"     : ["sum.jffs2"],
                "cramfs"        : ["cramfs"],
                "ext2"          : ["ext2"],
                "ext2.gz"       : ["ext2.gz"],
                "ext2.bz2"      : ["ext2.bz2"],
                "ext3"          : ["ext3"],
                "ext3.gz"       : ["ext3.gz"],
                "ext2.lzma"     : ["ext2.lzma"],
                "btrfs"         : ["btrfs"],
                "live"          : ["hddimg", "iso"],
                "squashfs"      : ["squashfs"],
                "squashfs-lzma" : ["squashfs-lzma"],
                "ubi"           : ["ubi"],
                "tar"           : ["tar"],
                "tar.gz"        : ["tar.gz"],
                "tar.bz2"       : ["tar.bz2"],
                "tar.xz"        : ["tar.xz"],
                "cpio"          : ["cpio"],
                "cpio.gz"       : ["cpio.gz"],
                "cpio.xz"       : ["cpio.xz"],
                "vmdk"          : ["vmdk"],
                "cpio.lzma"     : ["cpio.lzma"],
            }
        image_types = image_types.split()
        linkname = image_name +'-'+ curr_mach
        ret=[]
        for image_type in image_types:
           for real_image_type in supported_image_types.get(image_type,[]):
               linkpath = os.getcwd()+'/tmp/deploy/images/'+linkname+'.' + real_image_type
               if os.path.exists(linkpath):
                   readlink = os.readlink(linkpath)
                   stat = os.stat(linkpath)
                   image_info ={'image_name':readlink,
                                'size':'%.1f' % (stat.st_size*1.0/(1024*1024)) + ' MB',
                                }
                   ret.append(image_info)
        
        return json.dumps(ret)

def hob_conf_filter(fn, data):
    if fn.endswith("/local.conf"):
        distro = data.getVar("DISTRO_HOB")
        if distro:
            if distro != "defaultsetup":
                data.setVar("DISTRO", distro)
            else:
                data.delVar("DISTRO")

        keys = ["MACHINE_HOB", "SDKMACHINE_HOB", "PACKAGE_CLASSES_HOB", \
                "BB_NUMBER_THREADS_HOB", "PARALLEL_MAKE_HOB", "DL_DIR_HOB", \
                "SSTATE_DIR_HOB", "SSTATE_MIRROR_HOB", "INCOMPATIBLE_LICENSE_HOB"]
        for key in keys:
            var_hob = data.getVar(key)
            if var_hob:
                data.setVar(key.split("_HOB")[0], var_hob)
        return

    if fn.endswith("/bblayers.conf"):
        layers = data.getVar("BBLAYERS_HOB")
        if layers:
            data.setVar("BBLAYERS", layers)
        return

def main (server = None, eventHandler = None):
    server.runCommand(["setConfFilter", hob_conf_filter])
    WebServiceWrap.server = server
    WebServiceWrap.eventHandler = eventHandler

    host = ''
    port = 0
    for i in sys.argv[1:]:
        pattern = r'(\d+.\d+.\d+.\d+):(\d+)'
        match = re.match(pattern, i)
        if match:
            host = match.group(1)
            port = int(match.group(2))
            break
    if not host and not port:
            sys.exit('Fatal: using bitbake -u webhob_webservice ip:port\n')

    try:
        from wsgiref.simple_server import make_server
        server = make_server(host, port, Application([WebServiceWrap], 'tns'))
        print "Webservice UI runnning... \nWSDL is at: http://%s:%s/?wsdl" % (host, port)
        server.serve_forever()
    except ImportError:
        print "Fatal: webservice server code requires Python >= 2.5"

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(15)
    sys.exit(ret)

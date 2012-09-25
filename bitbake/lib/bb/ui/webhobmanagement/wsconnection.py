import sys
import traceback
try:
    from suds.client import Client, WebFault
except ImportError as e:
    sys.exit('Error:Install suds python lib firstly\n%s' % str(e))

try:
    import simplejson as json
except ImportError:
    import json

class Connection:
    def __init__(self, url, cache=None):
        self.url = url
        self.cache = cache
        self.client = Client(url, cache=self.cache)

    def runCommand(self, command):
        param_dict = {}
        param_list = []
        param_dict['function'] = command.pop(0)
        for i in command:
            if isinstance(i, list):
                param_list.append(('list'," ".join(i)))
            elif isinstance(i, bool):
                param_list.append(('bool',str(i)))
            elif isinstance(i, str):
                param_list.append(('string',str(i)))

        if param_list:
            param_dict['param_type'] = {'string':[t for t, p in param_list]}
            param_dict['params'] = {'string':[p for t, p in param_list]}

        try:
            return json.loads(self.client.service.runCommand(param_dict))
        except WebFault, f:
            traceback.print_exc()

    def getEvent(self):
        try:
            event = self.client.service.getEvent()
            if isinstance(event, unicode):
                event = event.encode('utf-8')
            o_event = json.loads(event)
            return o_event['events']
        except WebFault, f:
            traceback.print_exc()

    def get_images(self,image_name, curr_mach, image_types):
        try:
            event = self.client.service.get_images(image_name, curr_mach, image_types)
            if isinstance(event, unicode):
                event = event.encode('utf-8')
            o_event = json.loads(event)
            return o_event
        except WebFault, f:
            return 'ERROR:%s' % f
        except Exception, e:
            return 'ERROR:%s' % str(e)

if __name__ == '__main__':
    import sys
    import time
    from wsconnection import Connection
    from pprint import pprint

    params["core_base"] = self.runCommand(["getVariable", "COREBASE"]) or ""
    hob_layer = params["core_base"] + "/meta-hob"
    params["layer"] = self.runCommand(["getVariable", "BBLAYERS"]) or ""
    if hob_layer not in params["layer"].split():
        params["layer"] += (" " + hob_layer)

    server = Connection('http://localhost:8888/?wsdl')
    print server.runCommand(["getVariable", "BBLAYERS"])

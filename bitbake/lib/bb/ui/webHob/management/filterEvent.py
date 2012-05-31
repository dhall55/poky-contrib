'''
Created on 2012-5-16
@author: lvchunhx
'''
from utils.commond import getEvent
import settings,simplejson,types
from management.quartz import Quartz

class FilterEvent:

    def __init__(self, bitbake_ip, port, queue, build_flag):
        self.bitbake_ip = bitbake_ip
        self.port = port
        self.queue = queue
        self.build_flag = build_flag

    def handle_event(self):
        if self.build_flag == 'recipe':
            self.recipe_quartz = Quartz(1.0, self.recipe_event)
            self.recipe_quartz.start()
        elif self.build_flag =='package':
            self.package_quartz = Quartz(1.0, self.package_event)
            self.package_quartz.start()
        elif self.build_flag =='image':
            self.image_quartz = Quartz(1.0, self.image_event)
            self.image_quartz.start()

    def recipe_event(self):
        response = getEvent(self.bitbake_ip, self.port, settings.RESTFUL_API_EVENT_QUEUE)
        json = simplejson.loads(response)

        if json['queue']:
            for item in json['queue']:
                if type(item['value']) == types.DictType:
                    if len(self.queue) == 0:
                        if item['event'] == 'CommandCompleted':
                            continue
                    if item['event'] == 'TargetsTreeGenerated':
                        rcp_tree=open(settings.TEMPLATE_PATH+"/recipeTreeModel.txt",'w' )
                        rcp_tree.write(str(item['value']))
                        rcp_tree.close()

                        value_dict = {}
                        value_dict['event']=item['event']
                        value_dict['value']='TreeModel'
                        self.queue.append(value_dict)
                        self.recipe_quartz.cancel()
                    else:
                        value_dict = {}
                        value_dict['event']=item['event']
                        value_dict['value']=item['value']
                        self.queue.append(value_dict)
                else:
                    continue
        else:
            pass

    def package_event(self):
        response = getEvent(self.bitbake_ip, self.port, settings.RESTFUL_API_EVENT_QUEUE)
        json = simplejson.loads(response)

        if json['queue']:
            for item in json['queue']:
                if item['event'] == 'LogRecord':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'BuildStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'TaskStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'runQueueTaskStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'BuildCompleted':
                    pkg_tree=open(settings.TEMPLATE_PATH+"/packageTreeModel.txt",'w' )
                    pkg_tree.write(str(item['value']))
                    pkg_tree.close()
                    self.queue.append({'event':item['event'], 'value': 'TreeModel'})
                elif item['event'] == 'TaskFailed':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == "CommandFailed":
                    self.queue.append({'event': 'CommandFailed', 'value': 'failed'})
                elif item['event'] == "CommandCompleted":
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                    self.package_quartz.cancel()
                else:
                    continue
        else:
            pass

    def image_event(self):
        response = getEvent(self.bitbake_ip, self.port, settings.RESTFUL_API_EVENT_QUEUE)
        json = simplejson.loads(response)

        if json['queue']:
            for item in json['queue']:
                if item['event'] == 'LogRecord':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'BuildStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'TaskStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'runQueueTaskStarted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == 'BuildCompleted':
                    self.queue.append({'event':item['event'], 'value': 'complete'})
                    self.image_quartz.cancel()
                elif item['event'] == 'TaskFailed':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    self.queue.append(value_dict)
                elif item['event'] == "CommandFailed":
                    self.queue.append({'event': 'CommandFailed', 'value': 'failed'})
                else:
                    continue
        else:
            pass
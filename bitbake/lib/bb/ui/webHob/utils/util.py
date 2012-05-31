'''
Created on 2012-5-25
@author: lvchunhX
'''
import threading
import types
from hob.models import TreeModel
class storeTreeDataToDB(threading.Thread):

    def __init__(self, param, flag, operator):
        threading.Thread.__init__(self)
        self.param = param
        self.lock = threading.RLock()
        self.flag = flag
        self.operator = operator
        self.count = 0

    def run(self):
        self.lock.acquire()
        if type(self.param) == types.DictType:
            type_flag = ''
            if self.flag == "recipe":
                type_flag = self.flag
            elif self.flag == "task":
                type_flag = self.flag
            for key,value in self.param.iteritems():
                TreeModel(types=type_flag,name=key,license=str(value['license']),group=str(value['section']),description=str(value['summary']),is_included=False,operator=self.operator).save()
        elif type(self.param) == types.ListType:
            for val in self.param:
                TreeModel(types='baseimage',name=val, operator=self.operator).save()
        else:
            pass
        self.lock.release()
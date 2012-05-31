'''
Created on 2012-5-29
@author: lvchunhX
'''
import threading
import types
from hob.models import TreeModel, BuildConfig
class StorePackageDataToDB(threading.Thread):

    def __init__(self, dependency_list, tree_list, operator):
        threading.Thread.__init__(self)
        self.lock = threading.RLock()
        self.dependency_list = dependency_list
        self.tree_list = tree_list
        self.operator = operator
        self.count = 0

    def run(self):
        self.lock.acquire()
        for item in self.tree_list:
            if item['package'] in self.dependency_list:
                TreeModel(types='package', name=item['package'], pkg_parent=' ', is_included=True, operator=self.operator).save()
            else:
                TreeModel(types='package', name=item['package'], pkg_parent=' ', is_included=False, operator=self.operator).save()
            item['package_value'].sort()
            for val in item['package_value']:
                if str(val['pkg']) in self.dependency_list:
                    self.count = self.count + int(val['size'])
                    TreeModel(types='package',name=str(val['pkg']),group=str(val['section']),description=str(val['summary']),size=int(val['size']),pkg_parent=str(item['package']),is_included=True,operator=self.operator).save()
                else:
                    TreeModel(types='package',name=str(val['pkg']),group=str(val['section']),description=str(val['summary']),size=int(val['size']),pkg_parent=str(item['package']),is_included=False,operator=self.operator).save()
        self.count = self.count/1024
        BuildConfig.objects.filter(operator__username=self.operator.username, build_result = False).update(package_size=self.count)
        self.lock.release()
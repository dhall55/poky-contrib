'''
Created on 2012-5-20
@author: lvchunhX
'''
from management.models import Bitbakeserver

class AvailableBitbake():

    def __init__(self,queue):
        self.sharedata = queue

    def getBitbake(self):
        bitbakes = Bitbakeserver.objects.filter(status='0')
        for val in bitbakes:
            self.sharedata.append(val.name)
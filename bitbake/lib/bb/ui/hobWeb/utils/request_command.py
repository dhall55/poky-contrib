'''
Created on 2012-4-9

@author: lvchunhX
'''
import urllib2,urllib

def getEvent(ip,eventpath):
    url='http://'+ip+':8080'+eventpath
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

def sendRequest(ip,path,dict):
    url_params = urllib.urlencode(dict)
    url='http://'+ip+':8080'+path
    req = urllib2.Request(url,url_params)
    response = urllib2.urlopen(req)
    return response.read()

'''
Created on 2012-5-21
@author: lvchunhx
'''
import urllib2,urllib

def getEvent(ip, port, eventpath):
    url = 'http://%s:%d%s' % (ip, port, eventpath)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

def sendRequest(ip, port, path, dict):
    url_params = urllib.urlencode(dict)
    url = 'http://%s:%d%s' % (ip, port, path)
    req = urllib2.Request(url,url_params)
    response = urllib2.urlopen(req)
    return response.read()
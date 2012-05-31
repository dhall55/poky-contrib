'''
Created on 2012-5-10
@author: lvchunhx
'''
from django.shortcuts import render_to_response
from django.contrib import auth

def default(request):
    return render_to_response('login.html',locals())

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html',locals())

def error(request):
    error_msg = request.session.get("error_msg")
    return render_to_response('error.html',locals())
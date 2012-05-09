'''
Created on 2012-4-15

@author: lvchunhx
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bitbakeserver
from management.forms import BitbakeServerForm,LoginForm
from management.models import Operator
from utils.request_command import getEvent
import settings
import simplejson
from utils.manage_bitbake import TimerScheduler
import types
from hob.models import BuildConfig

def login(request,template_name="admin/admin_login.html"):
    return render_to_response(template_name,
                              locals(),
                              context_instance=RequestContext(request))

def add_server(request):
    if request.GET:
        id = request.GET['id']
        bitbakeServer = get_object_or_404(Bitbakeserver, pk=int(id))
    return render_to_response('admin/admin_addServer.html', locals())

def del_server(request):
    ids = request.REQUEST.getlist('checkbox')
    ids = [int(id) for id in ids]
    if ids:
        for id in ids:
            Bitbakeserver.objects.get(id=id).delete()
    return HttpResponseRedirect('/administrator/serverlist_disp/')

def saveOrupdate_server(request):
    form = BitbakeServerForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            if form.data['id']:
                bitbakeServer = get_object_or_404(Bitbakeserver, pk=int(form.data['id']))
                bitbakeServer.name = form.data['name']
                bitbakeServer.ip = form.data['ip']
                bitbakeServer.status = form.data['status']
                bitbakeServer.port = form.data['port']
                bitbakeServer.save()
                return HttpResponseRedirect('/administrator/serverlist_disp/')
            else:
                form.save()
                return HttpResponseRedirect('/administrator/serverlist_disp/')

def serverlist_disp(request):
    servers = Bitbakeserver.objects.all()
    return render_to_response('admin/admin_bitbakeServer.html', locals())

def del_user(request):
    ids = request.REQUEST.getlist('checkbox')
    ids = [int(id) for id in ids]
    if ids:
        for id in ids:
            operator = Operator.objects.get(id=id)
            User.objects.get(username=operator.username).delete()
            operator.delete()
    return HttpResponseRedirect('/administrator/userlist_disp/')

def userlist_disp(request):
    operators = Operator.objects.all()
    return render_to_response('admin/admin_users.html', locals())

def assign_Bitbakeserver(request):
    bitbakeserver = Bitbakeserver.objects.filter(status="0")
    return bitbakeserver

def update_Bitbake_status(request,id,status):
    Bitbakeserver.objects.filter(id=int(id)).update(status=status)
    return

def filter_recipeEvent(request,queue):
    ip = request.session.get("bitbake_ip")
    response = getEvent(ip,settings.RESTFUL_API_EVENT_QUEUE)
    json = simplejson.loads(response)

    if json['queue']:
        for item in json['queue']:
            if type(item['value']) == types.DictType:
                if len(queue) == 0:
                    if item['event'] == 'CommandCompleted':
                        continue
                if item['event'] == 'TargetsTreeGenerated':
                    '''
                    save recipe tree event
                    '''
                    rcp_tree=open(settings.TEMPLATE_PATH+"/recipeTreeModel.txt",'w' )
                    rcp_tree.write(str(item['value']))
                    rcp_tree.close()

                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']='TreeModel'
                    queue.append(value_dict)
                else:
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    queue.append(value_dict)

def filter_packageEvent(request,queue):
    ip = request.session.get("bitbake_ip")
    response = getEvent(ip,settings.RESTFUL_API_EVENT_QUEUE)
    json = simplejson.loads(response)
    if json['queue']:
        for item in json['queue']:
            if type(item['value']) == types.DictType or item['event'] == 'BuildStarted' or type(item['value']) == types.ListType:
                if len(queue) == 0:
                    if item['event'] == 'CommandCompleted':
                        continue
                if item['event'] == 'CacheLoadProgress' or \
                   item['event'] == 'BuildStarted' or \
                   item['event'] == 'runQueueTaskStarted' or \
                   item['event'] == 'TaskStarted' or \
                   item['event'] == 'TaskFailed' or \
                   item['event'] == 'CommandCompleted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    queue.append(value_dict)
                elif item['event'] == 'BuildCompleted':
                    '''
                    save package tree event
                    '''
                    rcp_tree=open(settings.TEMPLATE_PATH+"/packageTreeModel.txt",'w' )
                    rcp_tree.write(str(item['value']))
                    rcp_tree.close()

                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']='TreeModel'
                    queue.append(value_dict)
                else:
                    continue

def filter_imageEvent(request,queue):
    ip = request.session.get("bitbake_ip")
    response = getEvent(ip,settings.RESTFUL_API_EVENT_QUEUE)
    json = simplejson.loads(response)
    if json['queue']:
        for item in json['queue']:
            if type(item['value']) == types.DictType or item['event'] == 'BuildStarted' or type(item['value']) == types.ListType:
                if len(queue) == 0:
                    if item['event'] == 'CommandCompleted':
                        continue
                if item['event'] == 'CacheLoadProgress' or \
                   item['event'] == 'BuildStarted' or \
                   item['event'] == 'runQueueTaskStarted' or \
                   item['event'] == 'TaskStarted' or \
                   item['event'] == 'TaskFailed' or \
                   item['event'] == 'CommandCompleted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']=item['value']
                    queue.append(value_dict)
                elif item['event'] == 'BuildCompleted':
                    value_dict = {}
                    value_dict['event']=item['event']
                    value_dict['value']='Img_build_ok'
                    queue.append(value_dict)
                else:
                    continue

def user_server_mapping(request):
    operators = Operator.objects.all().exclude(bitbakeserver__isnull=True)
    return render_to_response('admin/user_server_mappinglist.html', locals())

def user_successful_cfg(request):
    build_cfgs = BuildConfig.objects.filter(build_result=True)
    return render_to_response('admin/admin_successful_buildconfig.html', locals())

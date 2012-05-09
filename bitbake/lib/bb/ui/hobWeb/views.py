'''
Created on 2012-4-24

@author: lvchunhx
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from management.forms import BitbakeServerForm,LoginForm
from management.models import Operator
from management.views import assign_Bitbakeserver, update_Bitbake_status

def login(request):
    form = LoginForm(request.POST)
    user = auth.authenticate(username=form.data['username'],
                             password=form.data['password'])
    if user is not None and user.is_active:
        auth.login(request, user)
        if form.data['flag'] == '1':
            if user.is_staff:
                return render_to_response('admin/admin_management.html', locals())
            else:
                error_msg = 'administrator role can login.'
                return render_to_response('error.html', locals())
        else:
            if Operator.objects.filter(username=form.data['username'])[0].bitbakeserver:
                bitbake = Operator.objects.filter(username=form.data['username'])[0].bitbakeserver
                param = '?name='+bitbake.name+'&ip='+bitbake.ip
                return HttpResponseRedirect('/hob/index/'+param)
            else:
                '''
                assign an idle bitbake to user
                '''
                bitbakeserver = assign_Bitbakeserver(request)
                if bitbakeserver:
                    operator = Operator.objects.filter(username=form.data['username']).update(bitbakeserver=bitbakeserver[0])
                    update_Bitbake_status(request,bitbakeserver[0].id,'1')
                    param = '?name='+bitbakeserver[0].name+'&ip='+bitbakeserver[0].ip
                    return HttpResponseRedirect('/hob/index/'+param)
                else:
                    return HttpResponseRedirect("/hob/login/")
    else:
        return HttpResponseRedirect("/invalid/")

def register(request):
    if request.GET:
        id = request.GET['id']
        operator = get_object_or_404(Operator, pk=int(id))
    return render_to_response('web/register.html', locals())

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html', locals())

def logerror(request):
    return render_to_response('error.html', locals())

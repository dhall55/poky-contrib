from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import auth
from hob.forms import LoginForm
from management.models import Operator, Bitbakeserver
from management.forms import userForm, BitbakeForm
from django.contrib.auth.models import User
from hob.models import BuildConfig

def admin_login(request):
    return render_to_response('admin/admin_login.html', locals())

def login(request):
    form = LoginForm(request.POST)
    user = auth.authenticate(username=form.data['username'],
                             password=form.data['password'])
    if user is not None and user.is_active:
        if user.is_staff and user.is_superuser:
            auth.login(request, user)
            return HttpResponseRedirect('/management/manage_list/')
        else:
            auth.logout(request)
            request.session["error_msg"] = form.data['username']+" is not administrator !"
            return HttpResponseRedirect('/error/')
    else:
        request.session["error_msg"] = form.data['username']+" is not exit or password not right !"
        return HttpResponseRedirect('/error/')

def manage_list(request):
    if request.user.is_authenticated():
        return render_to_response('admin/manageList.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def disp_UserList(request):
    if request.user.is_authenticated():
        operators = Operator.objects.all()
        return render_to_response('admin/userList.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def update_userInfo(request):
    if request.user.is_authenticated():
        operator = get_object_or_404(Operator, pk=int(request.GET['id']))
        return render_to_response('admin/userInfo.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def save_userInfo(request):
    form = userForm(request.POST)
    if form.is_valid():
        operator = get_object_or_404(Operator, pk=int(form.data['id']))
        user = User.objects.get(username=operator.username)
        user.set_password(form.data['password'])
        user.username = form.data['username']
        user.email = form.data['email']
        user.save()

        operator.username = form.data['username']
        operator.password = form.data['password']
        operator.email = form.data['email']
        operator.valid = form.data['valid']
        operator.status = form.data['status']
        operator.save()
    return HttpResponseRedirect('/management/disp_UserList/')

def remove_users(request):
    ids = request.REQUEST.getlist('checkbox')
    ids = [int(id) for id in ids]
    for val in Operator.objects.filter(id__in=ids):
        User.objects.filter(username = val.username).delete()
        val.delete()
    return HttpResponseRedirect('/management/disp_UserList/')

def disp_BitbakeList(request):
    if request.user.is_authenticated():
        bitbakes = Bitbakeserver.objects.all()
        return render_to_response('admin/bitbakeList.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def bitbakeInfo(request):
    if request.user.is_authenticated():
        if request.GET:
            bitbake = get_object_or_404(Bitbakeserver, pk=int(request.GET['id']))
        return render_to_response('admin/save_bitbake.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def save_bitbake(request):
    form = BitbakeForm(request.POST)
    if form.is_valid():
        if form.data['id']:
            bitbake = Bitbakeserver.objects.get(id = int(form.data['id']))
            bitbake.name = form.data['name']
            bitbake.ip = form.data['ip']
            bitbake.port = form.data['port']
            bitbake.status = form.data['status']
            bitbake.save()
        else:
            bitbake = Bitbakeserver.objects.filter(name=form.data['name'])
            if bitbake:
                request.session["error_msg"] = " bitbake name is used !"
            else:
                form.save()
                Bitbakeserver.objects.filter(name=form.data['name']).update(status='0')
    else:
        request.session["error_msg"] = " add or update userInfo error !"
    return HttpResponseRedirect('/management/disp_BitbakeList/')

def remove_bitbakes(request):
    ids = request.REQUEST.getlist('checkbox')
    ids = [int(id) for id in ids]
    Bitbakeserver.objects.filter(id__in=ids).delete()
    return HttpResponseRedirect('/management/disp_BitbakeList/')

def disp_BitbakeAndUserMapping(request):
    if request.user.is_authenticated():
        operators = Operator.objects.all().exclude(bitbakeserver__isnull=True)
        return render_to_response('admin/user_bitbake_mapping.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def disp_BuildConfig(request):
    if request.user.is_authenticated():
        configs = BuildConfig.objects.filter(build_result=True)
        return render_to_response('admin/buildconfigList.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')

def remove_BuildConfig(request):
    ids = request.REQUEST.getlist('checkbox')
    ids = [int(id) for id in ids]
    BuildConfig.objects.filter(id__in=ids).delete()
    return HttpResponseRedirect('/management/disp_BuildConfig/')

def disp_logs(request):
    if request.user.is_authenticated():
        return render_to_response('admin/logs.html', locals())
    else:
        request.session["error_msg"] = " please login first !"
        return HttpResponseRedirect('/error/')
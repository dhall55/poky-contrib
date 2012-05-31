from hob.forms import LoginForm
from django.shortcuts import render_to_response,get_object_or_404
from management.forms import userForm
from management.models import Operator, Bitbakeserver
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from Queue import Queue
from management.getAvailableBitbake import AvailableBitbake
from hob.models import BuildConfig

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            operator = Operator.objects.filter(username=form.data['username'],password=form.data['password'])
            if operator:
                user = auth.authenticate(username=form.data['username'],password=form.data['password'])
                if user is not None and user.is_active:
                    auth.login(request, user)
                    request.session["username"] = form.data['username']
                    if operator[0].bitbakeserver:
                        request.session["bitbake"] = operator[0].bitbakeserver
                    else:
                        queue = []
                        AvailableBitbake(queue).getBitbake()
                        if queue is None:
                            request.session["error_msg"] = "there is no bitbake to be used !"
                            return HttpResponseRedirect('/error/')
                        else:
                            bitbake = Bitbakeserver.objects.filter(name=queue.pop(0))[0]
                            bitbake.status = '1'
                            bitbake.save()
                            operator[0].bitbakeserver = bitbake
                            operator[0].save()
                            request.session["bitbake"] = bitbake
                    return HttpResponseRedirect('/hob/index/')
            else:
                request.session["error_msg"] = form.data['username']+" is not exist !"
                return HttpResponseRedirect('/error/')
    else:
        form = LoginForm()
        return render_to_response('login.html',locals())

def register(request):
    return render_to_response('web/register.html',locals())

def save_user(request):
    if request.method == 'POST':
        form = userForm(request.POST)
        if form.is_valid():
            if Operator.objects.filter(username=form.data['username']):
                request.session["error_msg"] = form.data['username']+" has already exist !"
                return HttpResponseRedirect('/error/')
            else:
                User.objects.create_user(username=form.data['username'],email=form.data['email'],password=form.data['password'])
                Operator(username = form.data['username'],\
                         password = form.data['password'],\
                         email = form.data['email'],\
                         valid = '1',\
                         status = '1').save()
    else:
        form = userForm()
    return HttpResponseRedirect('/')

def history_list(request):
    buildConfigs = BuildConfig.objects.filter(build_result=True)
    return render_to_response('web/history_list.html',locals())

def image_detail(request):
    id = int(request.GET.get("id"))
    buildConfig = BuildConfig.objects.filter(id=int(id))[0]
    recipes = buildConfig.recipes.strip().split(" ")
    packages = buildConfig.packages.strip().split(" ")
    return render_to_response('web/image_list.html',locals())
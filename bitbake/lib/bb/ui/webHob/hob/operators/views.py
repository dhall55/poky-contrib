from django.shortcuts import render_to_response
from hob.operators.forms import OperatorForm
from hob.operators.models import Operator, SystemConfig
from django.http import HttpResponseRedirect, HttpResponse

def register(request):
    return render_to_response('web/register.html',locals())

def save_user(request):
    form = OperatorForm(request.POST)
    if form.is_valid():
        operator = Operator.objects.filter(email=form.data['email'])
        if operator:
            error = operator[0].name + " is exist!"
            return render_to_response('web/register.html',locals())
        else:
            if len(SystemConfig.objects.filter(types='role', name='architect')) == 0:
                role = SystemConfig.objects.create(types='role', name='architect')
            else:
                role = SystemConfig.objects.get(types='role', name='architect')
            operator = Operator.objects.create(name=form.data['email'].split("@")[0],password=form.data['password'],email=form.data['email'],role=role)
    return HttpResponseRedirect("/")

def login(request):
    form = OperatorForm(request.POST)
    if form.is_valid():
        try:
            operator = Operator.objects.filter(email=form.data['email'],password=form.data['password'])
            if operator:
                print operator[0].is_login
                if operator[0].is_login == True:
                    error_message = form.data['email']+" is login!"
                    return render_to_response('web/index.html',locals())
                else:
                    operator[0].is_login=True
                    operator[0].save()
                    return HttpResponseRedirect("/hob/builds/index_dashboard/?current_user=%s" % str(operator[0].name))
            else:
                error_message = "email is not exist or password is error!"
                return render_to_response('web/index.html',locals())
        except:
            error_message = "unable to connect to database!"
            return render_to_response('web/index.html',locals())

def logout(request):
    current_user = request.GET["current_user"].strip()
    Operator.objects.filter(name=current_user).update(is_login=False)
    return HttpResponseRedirect("/")

def error(request):
    error_message = request.session.get("error_message")
    return render_to_response('web/error.html',locals())
from django.shortcuts import render_to_response
from django.contrib import auth
from hob.utils.xmlrpc_client import XmlrpcServer
from django.http import HttpResponseRedirect, HttpResponse
import simplejson,os
def index(request):
    return render_to_response('web/index.html',locals())

def admin_login(request):
    return render_to_response('web/admin_login.html',locals())

'''
admin management
'''
def admin_index(request):
    xmlRpc = XmlrpcServer("")
    try:
        bitbake_list = eval(xmlRpc.get_bitbake_all())
        username = request.POST["username"].strip()
        password = request.POST["password"].strip()
        user = auth.authenticate(username=username,password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if request.session.get("msg"):
                del request.session["msg"]
            else:
                msg = ""
            return render_to_response('web/admin_index.html',locals())
        else:
            error = "user name or password is error!"
            return render_to_response('web/admin_login.html',locals())
    except:
        if request.user.is_authenticated():
            username = request.user
            if request.session.get("msg"):
                msg = request.session.get("msg")
                del request.session["msg"]
            else:
                msg = ""
            return render_to_response('web/admin_index.html',locals())
        else:
            error = "unable to connect to database!"
            return render_to_response('web/admin_login.html',locals())

'''
remote connect bitbake
'''
def connect_bitbake(request):
    bitbake_ip = request.GET["bitbake_ip"].strip()
    bitbake_loginUser = request.GET["bitbake_loginUser"].strip()
    bitbake_password = request.GET["bitbake_password"].strip()

    result_dict = {"result":"ok", "set_bitbake_flag":"1", "bitbake_ip":bitbake_ip}
    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")

'''
add or update bitbake info.
'''
def edit_bitbake(request):
    bitbake_ip = request.POST["bitbake_ip"].strip()
    bitbake_port = request.POST["bitbake_port"].strip()

    url_git_clone = request.POST["url_git_clone"].strip()
    bitbake_repo = request.POST["bitbake_repo"].strip()
    bitbake_branch = request.POST["bitbake_branch"].strip()
    bitbake_commit = request.POST["bitbake_commit"].strip()
    url_nfs = request.POST["url_nfs"].strip()
    ip_documentServer = request.POST["ip_documentServer"].strip()
    url_image = request.POST["url_image"].strip()

    flag = request.POST["flag"]
    xmlRpc = XmlrpcServer("")
    if flag == "update":
        ip_old = request.POST["ip_old"].strip()
        ip_bitbake = request.POST["ip_bitbake"].strip()
        port_old = request.POST["port_old"].strip()
        if xmlRpc.update_bitbake(ip_bitbake, bitbake_port, ip_old, port_old):
            msg="update bitbake ok!"
        else:
            msg="update bitbake failed!"
    else:
        if xmlRpc.add_bitbake(bitbake_ip, bitbake_port):
            msg = "add bitbake(ip:"+bitbake_ip+") ok!"
        else:
            msg = "add bitbake(ip:"+bitbake_ip+") failed!"
    request.session["msg"]=msg
    return HttpResponseRedirect("/admin_index/")

'''
delete bitbake.
'''
def delete_bitbake(request):
    ip = request.GET["ip"].strip()
    port = request.GET["port"].strip()
    xmlRpc = XmlrpcServer("")
    if xmlRpc.remove_bitbake(ip, port):
        msg = "delete bitbake(ip:"+ip+") ok"
    else:
        msg = "delete bitbake(ip:"+ip+") failed"
    request.session["msg"]=msg
    return HttpResponseRedirect("/admin_index/")

'''
reset all bitbakes status.
'''
def reset_bitbake_all(request):
    xmlRpc = XmlrpcServer("")
    if xmlRpc.reset_bitbake_all():
        msg = "reset all bitbake are ok"
    else:
        msg = "reset all bitbake failed"
    request.session["msg"]=msg
    return HttpResponseRedirect("/admin_index/")


import simplejson
import pexpect


def index_install(request):
    ip = request.GET["ip"].strip()
    return render_to_response('web/admin_bitbake_install.html',locals())

def cmd_install(request):
    ip = request.POST.get('ip', None)
    passwd = request.POST.get('passwd', None)
    if ip is None or passwd is None:
        return HttpResponse(content='ip or password is empty', mimetype="text/plain")
    retval = ''
    path = os.path.dirname(__file__)
    retval+=_scp_cmd(ip, 'root', passwd, path+'/install' ,"/home/")
    _ssh_cmd(ip, 'root', passwd, "cp -r /home/install /home/builder/")
    _ssh_cmd(ip, 'root', passwd, "chown -R builder:builder /home/builder/install")
    _ssh_cmd(ip, 'root', passwd, "/home/install/install_root.sh > /home/install/install.log 2>&1 &")
    return HttpResponse(content=retval, mimetype="text/plain")

def get_install_log(request):
    ip = request.POST.get('ip', None)
    passwd = request.POST.get('passwd', None)
    if ip is None or passwd is None:
        return HttpResponse(content='ip or password is empty', mimetype="text/plain")
    retval = _ssh_cmd(ip, 'root', passwd, "cat /home/install/install.log")
    status = ''
    if 'Completed installation' in retval:
        status = 'Done'
#    return HttpResponse(content=retval, mimetype="text/plain")
    return HttpResponse(content=simplejson.dumps({'retval':retval,'status':status}), mimetype="text/json")

def cmd_start(request):
    ip = request.POST.get('ip', None)
    if ip is None:
        return HttpResponse(content='ip is empty', mimetype="text/plain")
    _ssh_cmd(ip, 'builder', 'builder123',"/home/builder/install/start_builder.sh >/home/builder/install/start.log 2>&1 &")
    return HttpResponse(content='Starting bitbake with webservice UI......', mimetype="text/plain")

def get_start_log(request):
    ip = request.POST.get('ip', None)
    if ip is None:
        return HttpResponse(content='ip is empty', mimetype="text/plain")
    retval = _ssh_cmd(ip, 'builder', 'builder123',"cat /home/builder/install/start.log")
    status = _ssh_cmd(ip, 'builder', 'builder123', "netstat -tln | grep 8888")
    status = status.strip()
    if status:
        status = 'Done'
#    return HttpResponse(content=retval, mimetype="text/plain")
    return HttpResponse(content=simplejson.dumps({'retval':retval,'status':status}), mimetype="text/json")

def stop(request):
    ip = request.POST.get('ip', None)
    if ip is None:
        return HttpResponse(content='ip  is empty', mimetype="text/plain")
    _ssh_cmd(ip, 'builder', 'builder123', "ps aux | grep bitbake | grep -v grep | awk '{print $2}' | xargs kill -9")
    return HttpResponse(content='Bitbake stopped', mimetype="text/plain")

def status(request):
    ip = request.POST.get('ip', None)
    if ip is None:
        return HttpResponse(content='ip is empty', mimetype="text/plain")
    retval = _ssh_cmd(ip, 'builder', 'builder123', "ps aux | grep bitbake | grep -v grep")
    retval = retval.strip()
    if retval:
        status = "bitbake Running"
    else:
        status = "bitbake is not running"
    return HttpResponse(content=simplejson.dumps({'retval':retval,'status':status}), mimetype="text/json")

def _scp_cmd(r_host, r_user, r_passwd, frompath, tofolder):
    command='scp -r %s %s@%s:%s'%(frompath, r_user, r_host, tofolder)
    ssh = pexpect.spawn(command)
    r = ''
    try:
        i = ssh.expect(['password: ', 'continue connecting (yes/no)?'])
        if i == 0 :
            ssh.sendline(r_passwd)
        elif i == 1:
            ssh.sendline('yes')
    except pexpect.EOF:
        ssh.close()
    else:
        r = ssh.read()
        ssh.expect(pexpect.EOF)
        ssh.close()
    return r

def _ssh_cmd(ip, user, passwd, cmd):
    ssh = pexpect.spawn('ssh %s@%s "%s"' % (user, ip, cmd))
    r = ''
    try:
        i = ssh.expect(['password: ', 'continue connecting (yes/no)?'],timeout=5)
        if i == 0 :
            ssh.sendline(passwd)
        elif i == 1:
            ssh.sendline('yes')
    except pexpect.EOF:
        ssh.close()
    else:
        r = ssh.read()
        ssh.expect(pexpect.EOF)
        ssh.close()
    return r
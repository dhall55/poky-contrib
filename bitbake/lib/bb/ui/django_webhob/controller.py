import simplejson
import types
from django.shortcuts import render_to_response
from django.http import HttpResponse
from model import getConfig
from model import rcp_dep_include
from model import pkg_dep_include
from model.db_test import mysql_update, mysql_select
import time

G_asyncconfigs = {}

def index(request):
    ssyncconfs = getConfig.getssyncConfigss()
    global G_asyncconfigs;
    G_asyncconfigs['format'] = ssyncconfs['pclass'].split('_')[1].strip()
    G_asyncconfigs['sdk_machine'] = ssyncconfs['sdk_machine']
    G_asyncconfigs['distro'] = ssyncconfs['distro']
    return render_to_response('index.html', {'ssyncconfs':ssyncconfs})

def send_command_asynconfs(request):
    return HttpResponse(getConfig.req_url(path='action/asyncconfs'))

def send_command_parserecipe(request):
    retValue = None
    configs = {
        'layers': request.REQUEST.getlist('layers'),
        'curr_package_format': request.REQUEST.getlist('formats'),
        'sstatedir': request.POST.get('sstatedir',''),
        'sstatemirror': request.POST.get('sstatemirror',''),
        'bbthread': request.POST.get('bbthread',''),
        'image_extra_size': request.POST.get('image_extra_size',''),
        'incompat_license': request.POST.get('incompat_license',''),
        'curr_distro': request.POST.get('distros',''),
        'dldir': request.POST.get('dldir',''),
        'pmake': request.POST.get('pmake',''),
        'curr_mach': request.POST.get('machines',''),
        'curr_sdk_machine': request.POST.get('machines_sdk',''),
        'image_addr': request.POST.get('image_addr',''),
    }
    apiretvalue = getConfig.req_url(path='action/parserecipe', method='post', params=configs)
    o_apiretvalue = simplejson.loads(apiretvalue)
    if o_apiretvalue['status'] == 'OK':
        mysql_update('user_configs', 'configs', str(configs))
    return HttpResponse(content=apiretvalue, mimetype="text/plain")

def getAsynconfsEvents(request):
    json = simplejson.loads(getConfig.req_url(path='action/getevents'))
    q = json['queue']
    retval = {}
    for item in q:
        if item['value'] and type(item['value']) == types.DictType:
            for k, v in item['value'].iteritems():
                str = ''
                for async_item in v:
                    if k == 'formats':
                        if G_asyncconfigs.get('format', '') == async_item:
                            str+= "<input type='checkbox' name='%s' value='%s' checked /> %s" \
                                    % (k, async_item, async_item)
                        else:
                            str+= "<input type='checkbox' name='%s' value='%s' /> %s" \
                                    % (k, async_item, async_item)
                    else:
                        if (G_asyncconfigs.get('distro', '') == async_item or \
                            G_asyncconfigs.get('sdk_machine', '') == async_item) \
                            and k!= 'machines':
                            str+= "<option value='%s' selected='selected'>%s</option>\n" \
                                    % (async_item,async_item)
                        else:
                            str+= "<option value='%s'>%s</option>\n" % (async_item,async_item)
                retval[k]=str
        elif item['event'] == "CommandCompleted":
            retval['action']='OK'
    return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")

def getParseRecipeEvents(request):
    json = simplejson.loads(getConfig.req_url( path='action/getevents'))
    q = json['queue']
    base_images = None
    pct = None
    retval = {}
    for item in q:
        if item['event'] == "TargetsTreeGenerated":
            rcp_model = item['value']['model']
            mysql_update('rcp_model', 'rcp_model', str(rcp_model))
            strhtml=''
            base_image_list = []
            for item in rcp_model["pn"]:
                if '-image-' in item:
                    base_image_list.append(item)
            base_image_list.sort()
            for item in base_image_list:
                strhtml+= "<option value='%s'>%s</option>\n" % (item, item)
            base_images = strhtml
        else:
            if item['event'].endswith('Started'):
                if item['event'] == "TreeDataPreparationStarted":
                    pct = 60
                else:
                    pct = 0
            elif item['event'].endswith('Progress'):
                if item['event'] == "TreeDataPreparationProgress":
                   pct = 60 + int(item['value']['current']*40.0/item['value']['total'])
                else:
                   pct = int(item['value']['current']*60.0/item['value']['total'])
            elif item['event'].endswith('Completed'):
                if item['event'] == "TreeDataPreparationCompleted":
                    pct = 100
                else:
                    pct = 60
    if pct:
        retval= {'status':'parsing', 'value': pct}
    if base_images:
        retval= {'action': 'DONE', 'baseimage':base_images}
    return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")

def recipe_list_page(request):
    rcps = {}
    rcps_tasks = {}
    details = {}
    dep_list = []
    reload(rcp_dep_include)
    baseimg = request.GET.get('baseimg','').strip()
    rcp_model = eval(mysql_select('rcp_model')[1])
    if rcp_model:
        if baseimg and baseimg!='diy':
            dep_list = rcp_dep_include.select_base_image_dep(baseimg,rcp_model)
            dep_list.sort()
        for item in rcp_model["pn"]:
            if ('task-' not in item and '-image-' not in item and 'meta-'
                not in item and 'lib32-' not in item and 'lib64-'
                not in item and '-native' not in item):
                rcps[item] = rcp_model["pn"][item]
                rcps[item]['include'] = False
            if ('task-' in item):
                summary = rcp_model["pn"][item]["summary"]
                lic = rcp_model["pn"][item]["license"]
                group = rcp_model["pn"][item]["section"]
                if ('lib32-' in item or 'lib64-' in item):
                    atype = 'mltask'
                else:
                    atype = 'task'
                for pkg in rcp_model["pn"][item]["packages"]:
                    details[pkg] = pkg
                    details['summary'] = summary
                    details['license'] = lic
                    details['section'] = group
                    rcps_tasks[pkg] = details
                    rcps_tasks[pkg]['include'] = False
        for item in dep_list:
            if item in rcps.keys():
                rcps[item]['include'] = True
            if item in rcps_tasks.keys():
                rcps_tasks[item]['include'] = True
        sort_rcps = sorted(rcps.items(), key=lambda d: d[0])
        sort_rcps_tasks = sorted(rcps_tasks.items(), key=lambda d: d[0])
        return render_to_response('recipe_list_page.html',
                                  {'sort_rcps':sort_rcps,
                                   'sort_rcps_total':len(sort_rcps),
                                   'sort_rcps_tasks': sort_rcps_tasks,
                                   'sort_rcps_tasks_total': len(sort_rcps_tasks),
                                   'dep':{'dep_list':dep_list,'dep_len':len(dep_list) },
                                   'baseimg':baseimg,
                                   })
    else:
        return HttpResponse(content='error', mimetype="text/plain")

def ajax_rcp_include(request):
    reload(rcp_dep_include)
    rcp_item = request.GET.get('rcp_item','').strip()
    rcp_model = eval(mysql_select('rcp_model')[1])
    dep_list = []
    dep_list_d = []
    if rcp_model and rcp_item:
        dep_list = rcp_dep_include.include_rcp_dep(rcp_item,rcp_model)
        for item in dep_list:
            dep_list_d.append({'item':item})
    return HttpResponse(content=simplejson.dumps({'rcp_list':dep_list_d, 'rcp_list_len':len(dep_list_d)}), mimetype="text/plain")

def ajax_pkg_include(request):
    reload(pkg_dep_include)
    rcp_item = request.GET.get('rcp_item','').strip()
    rcp_model = eval(mysql_select('pkg_model')[1])
    dep_list = []
    dep_list_d = []
    if rcp_model and rcp_item:
        dep_list = pkg_dep_include.include_pkg_child_dep(rcp_item, rcp_model)
        for item in dep_list:
            dep_list_d.append({'item':item})
    return HttpResponse(content=simplejson.dumps({'rcp_list':dep_list_d, 'rcp_list_len':len(dep_list_d)}), mimetype="text/plain")

def send_command_buildpackage(request):
    reload(rcp_dep_include)
    user_rcp_list = request.POST.get('user_rcp_list','').strip().strip(',')
    r_l_baseimg = request.POST.get('r_l_baseimg','').strip()
    baseimg = ''
    if not user_rcp_list:
        baseimg = request.GET.get('baseimg','').strip()
        rcp_model = mysql_select('rcp_model')[1]
        if not rcp_model:
            return HttpResponse(content='rcp_model is empty', mimetype="text/plain")
        rcp_model = eval(rcp_model)
        if baseimg:
            dep_list = rcp_dep_include.select_base_image_dep(baseimg,rcp_model)
            dep_list.sort()
        else:
            return HttpResponse(content='baseimg is empty', mimetype="text/plain")
    else:
        user_rcp_list = list(set(user_rcp_list.split(', ')))
    configs = mysql_select('user_configs')[1]
    if not configs:
        return HttpResponse(content='configs is empty in db', mimetype="text/plain")
    configs = eval(configs)
    if not user_rcp_list:
        configs['rcp_list'] = dep_list
    else:
        configs['rcp_list'] = user_rcp_list
    apiretvalue = getConfig.req_url(path='action/buildpkg', method='post', params=configs)
    o_apiretvalue = simplejson.loads(apiretvalue)
    if o_apiretvalue['status'] == 'OK':
        mysql_update('user_configs', 'rcp_list', str(configs['rcp_list']))
        rcp_model = eval(mysql_select('rcp_model')[1])
        if r_l_baseimg:
            pkg_list = rcp_model["rdepends-pn"].get(r_l_baseimg, [])
            mysql_update('user_configs', 'pkg_list', str(pkg_list))
        elif baseimg:
            pkg_list = rcp_model["rdepends-pn"].get(baseimg, [])
            mysql_update('user_configs', 'pkg_list', str(pkg_list))
        else:
            mysql_update('user_configs', 'pkg_list', '')
        return render_to_response('build_pkg.html',{})
    else:
        return HttpResponse(content=apiretvalue, mimetype="text/plain")

def getBuildPackageEvents(request):
    retval={}
    logq = []
    error = []
    pct = None
    logRecord_conf = ''
    treedata = ''
    CommandFailed = None
    json = simplejson.loads(getConfig.req_url( path='action/getevents'))
    q = json['queue']
    for item in q:
        if item['event'] == "runQueueTaskStarted":
            pct = int(item['value']['num_of_completed']*100.0/item['value']['total'])
        elif item['event'] == "LogRecord":
            logRecord = str(item['value']).strip()
            if logRecord.startswith('OE Build') or logRecord.startswith('Resolving') or \
               logRecord.startswith('Executing RunQueue Tasks') or logRecord.startswith('Tasks Summary'):
                logRecord_conf+= logRecord
        elif item['event'] == "TaskStarted":
            logq.append({'package':item['value']['package'], 'task': item['value']['task']})
            retval['building_log'] = logq
        elif item['event'] == "BuildStarted":
            logRecord_conf+= "\nBuild Started (%s)\n" % time.strftime('%m/%d/%Y %H:%M:%S')
        elif item['event'] == "BuildCompleted":
            pct = 100
            id = 0
            include = ''
            treedata = ''
            selected_pkg_size = 0
            selected_pkg = []
            selected_pkg_str = ''
            dep_pkg_list = []
            sort_res = item['value']
            sort_res.sort()
            mysql_update('pkg_model', 'pkg_model', str(sort_res))
            pkg_list = mysql_select('user_configs')[3]
            if pkg_list:
                pkg_list = eval(pkg_list)
                for item in pkg_list:
                    dep_pkg_list+= pkg_dep_include.include_pkg_child_dep(item, sort_res)
            dep_pkg_list = list(set(dep_pkg_list))
            treedata="<table>"
            for item in sort_res:
                id+= 1
                if item['package'] in dep_pkg_list:
                    include = 'checked'
                else:
                    include = ''
                treedata+= "<tr><td width='10%'>"+str(id)+"</td><td width='45%'>"
                treedata+= str(item['package'])[0:70]+"</td><td width='25%'>&nbsp;</td>"
                treedata+= "<td width='20%'><!--input type='checkbox' "+include+" /--></td></tr>\n"
                for inneritem in item['package_value']:
                    if inneritem['pkg'] in dep_pkg_list:
                        include = 'checked'
                        selected_pkg.append(inneritem['pkg'])
                        selected_pkg_size+= int(inneritem['size'])
                    else:
                        include = ''
                    treedata+= "<tr><td width='10%'>&nbsp;</td><td width='45%'>"
                    treedata+= "--->"+str(inneritem['pkg'])+"</td><td width='25%'>"
                    treedata+= str(inneritem['size'])+"KB</td><td width='20%'>"
                    treedata+= "<input name='include_item' value='"
                    treedata+= str(inneritem['pkg'])+"' type='checkbox' "
                    treedata+= include+" onclick='select_plk(this)' /></td></tr>\n"
            treedata+="</table>"
            html_str = ''
            for item in selected_pkg:
                html_str+= item+', '
            selected_pkg_str = '''<h3 >Selected <span class='selected_items'>%s
                                  (%sM)</span> packages</h3>
                                  <div class='selectedrecipes'>%s</div>
                               ''' % (len(list(set(selected_pkg))), int(selected_pkg_size/1024), html_str)
            html_str = ''
            logRecord_conf+= "\nBuild Completed (%s)\n" % time.strftime('%m/%d/%Y %H:%M:%S')
        elif item['event'] == "CommandCompleted":
            pct = None
        elif item['event'] == "TaskFailed":
            s = item['value']['logdata']
            error.append({'error': s[s.index('ERROR'):-1]})
            retval['error'] =  error
            return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")
        elif item['event'] == "CommandFailed":
            CommandFailed = 'failed'
        if pct:
            retval['pct']= pct
        if logRecord_conf:
            retval['logRecord_conf'] = logRecord_conf
        if logq:
             retval['building_log'] = logq
        if error:
            retval['error'] =  error
        if treedata:
            retval['action'] =  'DONE'
            retval['treedata'] =  treedata
            if selected_pkg_str:
                retval['selected_pkg_str'] =  selected_pkg_str
        if CommandFailed:
            retval['CommandFailed'] =  CommandFailed
    return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")

def send_command_buildimage(request):
    user_pkg_list = request.POST.get('user_pkg_list','').strip().strip(',')
    if not user_pkg_list:
        baseimg = request.GET.get('baseimg','').strip()
        rcp_model = mysql_select('rcp_model')[1]
        if not rcp_model:
            return HttpResponse(content='rcp_model is empty', mimetype="text/plain")
        rcp_model = eval(rcp_model)
        if baseimg:
            dep_list = rcp_dep_include.select_base_image_dep(baseimg,rcp_model)
            dep_list.sort()
        else:
            return HttpResponse(content='baseimg is empty', mimetype="text/plain")
    else:
        user_pkg_list = list(set(user_pkg_list.split(', ')))
    configs = mysql_select('user_configs')[1]
    if not configs:
        return HttpResponse(content='configs is empty in db', mimetype="text/plain")
    configs = eval(configs)
    if not user_pkg_list:
        configs['rcp_list'] = dep_list
        configs['pkg_list'] = rcp_model["rdepends-pn"].get(baseimg, [])
        configs['fast_mode'] = True
    else:
        rcp_list = mysql_select('user_configs')[2]
        if rcp_list:
            rcp_list = eval(rcp_list)
        else:
            return HttpResponse(content='rcp_list is empty in db', mimetype="text/plain")
        configs['rcp_list'] = rcp_list
        configs['pkg_list'] = user_pkg_list
        configs['fast_mode'] = False
    mysql_update('user_configs', 'all_configs', str(configs))
    apiretvalue = getConfig.req_url(path='action/buildimage', method='post', params=configs)
    apiretvalue = simplejson.loads(apiretvalue)
    if apiretvalue['status'] == 'OK':
        return render_to_response('build_image.html',{})
    else:
        return HttpResponse(content=apiretvalue, mimetype="text/plain")

def getBuildimageEvents(request):
    retval={}
    logq = []
    error = []
    pct = None
    logRecord_conf = ''
    treedata = ''
    CommandFailed = None
    json = simplejson.loads(getConfig.req_url( path='action/getevents'))
    q = json['queue']
    for item in q:
        if item['event'] == "runQueueTaskStarted":
            pct = int(item['value']['num_of_completed']*100.0/item['value']['total'])
        elif item['event'] == "LogRecord":
            logRecord = str(item['value']).strip()+'\n'
            if logRecord.startswith('OE Build') or logRecord.startswith('Resolving') or \
               logRecord.startswith('Executing RunQueue Tasks') or logRecord.startswith('Tasks Summary'):
                logRecord_conf+= logRecord
        elif item['event'] == "TaskStarted":
            logq.append({'package':item['value']['package'], 'task': item['value']['task']})
            retval['building_log'] = logq
        elif item['event'] == "BuildStarted":
            logRecord_conf+= "\nBuild Started (%s)\n" % time.strftime('%m/%d/%Y %H:%M:%S')
        elif item['event'] == "BuildCompleted":
            pct = 100
            iscache = False
            logRecord_conf+= "\nBuild Completed (%s)\n" % time.strftime('%m/%d/%Y %H:%M:%S')
        elif item['event'] == "CommandCompleted":
            pct = None
            configs = mysql_select('user_configs')[1]
            configs = eval(configs)
            treedata+= '<h3>Generated images list</h3><table><tr>'
            treedata+= '<th>image Name</th><th>Ctime</th><th>Size</th><th>Download Address</th></tr>'
            image_addr = configs['image_addr']
            import os
            cmd  = os.popen("ls -lth %s | grep -E '^(-).*?(bz2|ext3|bin)$' | awk \'{print $9, $7\"/\"$6,$8,$5}\'" % image_addr)
            ci=0
            while True:
                ci+=1
                line = cmd.readline().strip().split()
                if not line or ci>2:
                    break
                treedata+='<tr><td>%s</td><td>%s %s</td><td>%s</td><td><a href="#">download</a></td></tr>' % (line[0],line[1],line[2],line[3])
            treedata+='<tr><td>kernel(not real)</td><td>------</td><td>-------</td><td><a href="#">download</a></td></tr>'
            treedata+='<tr><td>sdk(not real)</td><td>------</td><td>-------</td><td><a href="#">download</a></td></tr>'
            treedata+='</table>'
            all_configs  = mysql_select('user_configs')[4]
            all_configs = eval(all_configs)
            layer_forstr = ''
            treedata+="<h3 style='margin-top:20px'>Save configuration as a template</h3><ul>"
            for k,v in all_configs.iteritems():
                if k in ('layers', 'curr_sdk_machine', 'bbthread',
                         'image_extra_size','curr_package_format',
                         'rcp_list','pkg_list','curr_mach','fast_mode',
                         'pmake','incompat_license','curr_distro'):
                    if k=='rcp_list' or k=='pkg_list':
                        v=", ".join(v)
                        if len(v)>150:
                            v=v[0:150]
                        v = '%s ....<a href="#">View all</a>' % v
                    elif k=='layers':
                        v = "meta, meta-yocto"
                    treedata+="<li><span class='k'>%s:</span><p class='v'>%s</p>" % (k,v)
            treedata+='<li style="width:95%; font-weight:bold;">'
            treedata+='<a href="/" style="float:left">Home page</a>'
            treedata+='<a href="#" style="float:right">'
            treedata+='Edit and Save current configuration as a template</a></li></ul>'
        elif item['event'] == "TaskFailed":
            s = item['value']['logdata']
            error.append({'error': s[s.index('ERROR'):-1]})
            retval['error'] =  error
            return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")
        elif item['event'] == "CommandFailed":
            CommandFailed = 'failed'
        if pct:
            retval['pct']= pct
        if logRecord_conf:
            retval['logRecord_conf'] = logRecord_conf
        if logq:
             retval['building_log'] = logq
        if error:
            retval['error'] =  error
        if treedata:
            retval['action'] = 'DONE'
            retval['treedata'] =  treedata
        if CommandFailed:
            retval['CommandFailed'] =  CommandFailed
    return HttpResponse(content=simplejson.dumps(retval), mimetype="text/plain")

def history_list(request):
    import os
    shell_str = "ls -lth /home/xiaotong/workspace/build_demo/tmp/deploy/images | grep -E '^(-).*?(bz2|ext3|bin)$' | awk \'{print $9, $7\"/\"$6,$8,$5}\'"
    cmd  = os.popen(shell_str)
    history_list=[]
    while True:
        line = cmd.readline().strip().split()
        if not line:
            break
        items = (line[0],line[1],line[2], line[3])
        history_list.append(items)
    return render_to_response('history_list.html',{'history_list':history_list})

def api(request):
     return render_to_response('restApiHtml.html',{})

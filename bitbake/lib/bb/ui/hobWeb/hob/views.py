'''
Created on 2012-4-10

@author: lvchunhx
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.models import User
from management.forms import LoginForm, BitbakeServerForm
from management.models import Operator,Bitbakeserver
import settings,simplejson,types,logging
from urllib2 import URLError
from utils.request_command import getEvent, sendRequest
from hob.models import BuildConfig, SystemConfig, TreeModel
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from management.views import filter_recipeEvent, filter_packageEvent,\
    filter_imageEvent
from utils import commons

def login(request,template_name="login.html"):
    return render_to_response(template_name,
                              locals(),
                              context_instance=RequestContext(request))
'''
obtain synchronous data,such as package_format,image_rootfs
build_toolchain,distro,bb_number_threads,parallel_make,
download_directory,sstate_directory,sstate_mirror,layers,
store data into db.
'''
def index(request,template_name="index.html"):
    form = BitbakeServerForm(request.GET)
    try:
        bitbake = Bitbakeserver.objects.filter(name=form.data['name'])
        operator = Operator.objects.filter(bitbakeserver=bitbake[0])
        if BuildConfig.objects.filter(operator=operator[0],build_result=False):
            pass
        else:
            str_packagingformat = getEvent(form.data['ip'],settings.RESTFUL_API_PACKING_FORMAT)
            packagingformat = eval(str_packagingformat)['PACKAGE_CLASSES'].lstrip('package_')

            str_imageRootfs = getEvent(form.data['ip'],settings.RESTFUL_API_IMAGE_ROOTFS_SIZE)
            imageRootfs = eval(str_imageRootfs)['IMAGE_ROOTFS_EXTRA_SPACE'].strip()

            str_buildToolchain = getEvent(form.data['ip'],settings.RESTFUL_API_BUILD_TOOLCHAIN)
            buildToolchain = eval(str_buildToolchain)['SDK_ARCH']

            str_distro = getEvent(form.data['ip'],settings.RESTFUL_API_DISTRO)
            distro = eval(str_distro)['DISTRO']

            str_bbNumberThread = getEvent(form.data['ip'],settings.RESTFUL_API_BB_NUMBER_THREADS)
            bbNumberThread = eval(str_bbNumberThread)['BB_NUMBER_THREADS'].strip()
            if bbNumberThread == '':
                bbNumberThread = 4

            str_parallelMake = getEvent(form.data['ip'],settings.RESTFUL_API_PARALLEL_MAKE)
            parallelMake = eval(str_parallelMake)['PARALLEL_MAKE'].strip()
            if parallelMake == '':
                parallelMake = 4

            str_downloadDir = getEvent(form.data['ip'],settings.RESTFUL_API_DOWNLOAD_DIRECTORY)
            downloadDir = eval(str_downloadDir)['DL_DIR'].strip()

            str_sstateDir = getEvent(form.data['ip'],settings.RESTFUL_API_SSTATE_DIRECTORY)
            sstateDir = eval(str_sstateDir)['SSTATE_DIR'].strip()

            str_sstateMirror = getEvent(form.data['ip'],settings.RESTFUL_API_SSTATE_MIRROR)
            sstateMirror = eval(str_sstateMirror)['SSTATE_MIRROR'].strip()

            str_layers = getEvent(form.data['ip'],settings.RESTFUL_API_LAYERS)
            layers = eval(str_layers)['BBLAYERS'].strip()

            BuildConfig(operator=operator[0],
                        bitbakeserver=bitbake[0],
                        package_format=packagingformat,
                        image_rootfs=int(imageRootfs),
                        build_toolchain=buildToolchain,
                        distro=distro,
                        bb_number_threads=int(bbNumberThread),
                        parallel_make=int(parallelMake),
                        download_directory=downloadDir,
                        sstate_directory=sstateDir,
                        sstate_mirror=sstateMirror,
                        layers=layers).save()
    except URLError:
        return HttpResponseRedirect('/invalid/')
    request.session["bitbake_ip"]=form.data['ip']
    request.session['current_operator']=operator[0].username
    return render_to_response(template_name,
                              locals(),
                              context_instance=RequestContext(request))
'''
create new user or update user's basic info
'''
def saveOrupdate_user(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        if form.data['id']:
            operator = get_object_or_404(Operator, pk=int(form.data['id']))
            user = User.objects.get(username=operator.username)
            user.set_password(form.data['password'])
            user.username = form.data['username']
            user.email = form.data['email']
            user.save()

            operator.username = user.username
            operator.password = user.password
            operator.email = user.email
            operator.valid = form.data['valid']
            operator.save()
            return HttpResponseRedirect('/administrator/userlist_disp/')
        else:
            user = User.objects.create_user(username=form.data['username'],
                                            email=form.data['email'],
                                            password=form.data['password'])
            Operator(username=user.username,
                     email=user.email,
                     password=user.password,
                     valid=form.data['valid']).save()
            return HttpResponseRedirect('/hob/login/')

'''
send asynchronous request, obtain machines,distros,machines-sdk,formats list
'''
def config_request(request):
    ip = request.session.get("bitbake_ip")
    response = getEvent(ip,settings.RESTFUL_API_SYSTEM_CONFIG_REQUEST)
    return HttpResponse(response)

def get_configEvents(request):
    ip = request.session.get("bitbake_ip")
    response = getEvent(ip,settings.RESTFUL_API_EVENT_QUEUE)
    json = simplejson.loads(response)

    config_dict = {}
    for item in json['queue']:
        if item['value'] and type(item['value']) == types.DictType:
            for key, value in item['value'].iteritems():
                if type(value) == types.ListType:
                    option = ''
                    for temp in value:
                        if SystemConfig.objects.filter(name=temp):
                            pass
                        else:
                            SystemConfig(name=temp,types=key).save()
                        if 'machines' == key:
                            option += "<option value='%s'>%s</option>\n" % (temp,temp)
                            config_dict[key] = option
                else:
                    config_dict[key] = value
    return HttpResponse(content=simplejson.dumps(config_dict), mimetype="text/plain")

def parseRecipe_request(request):
    ip = request.session.get("bitbake_ip")
    machine = request.POST['machine']
    bitbake = Bitbakeserver.objects.filter(ip=ip)[0]
    BuildConfig.objects.filter(bitbakeserver=bitbake,build_result=False).update(machine=machine)
    operator_config = BuildConfig.objects.filter(bitbakeserver=bitbake,build_result=False)[0]

    build_config = {}
    build_config['layers'] = operator_config.layers.split(' ')
    build_config['curr_mach'] = machine
    build_config['curr_package_format'] = operator_config.package_format.split(',')
    build_config['curr_distro'] = operator_config.distro
    build_config['imageRoot'] = operator_config.image_rootfs
    build_config['image_extra_size'] = operator_config.image_extra
    build_config['curr_sdk_machine'] = operator_config.build_toolchain
    build_config['bbthread'] = operator_config.bb_number_threads
    build_config['pmake'] = operator_config.parallel_make
    build_config['dldir'] = operator_config.download_directory
    build_config['sstatedir'] = operator_config.sstate_directory
    build_config['sstatemirror'] = operator_config.sstate_mirror
    build_config['incompat_license'] = ''
    build_config['extra_setting'] = {}

    response=sendRequest(ip,settings.RESTFUL_API_PARSE_RECIPE,build_config)
    status = simplejson.loads(response)
    return HttpResponse(content=simplejson.dumps(status), mimetype="text/plain")

def parseRecipe_event(request):
    queue = []
    filter_recipeEvent(request,queue)
    events = {}
    recipes_dict = {}
    baseimgs_dict = {}
    tasks_dict = {}
    if queue:
        for item in queue:
            if item['event'] == "TargetsTreeGenerated":
                tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
                tree_str = tree_file.read()
                tree_file.close()

                tree_dict = eval(tree_str)
                tree_model = tree_dict['model']

                for val in tree_model['pn']:
                    if ('task-' not in val \
                        and '-image-' not in val \
                        and 'meta-' not in val \
                        and 'lib32-' not in val \
                        and 'lib64-' not in val \
                        and '-native' not in val):
                        recipes_dict[val]=tree_model['pn'][val]
                    if 'task-' in  val and  val not in tasks_dict.keys():
                        task_dict = {}
                        task_dict[val] = val
                        task_dict['summary'] = tree_model["pn"][val]["summary"]
                        task_dict['license'] = tree_model["pn"][val]["license"]
                        task_dict['section'] = tree_model["pn"][val]["section"]
                        tasks_dict[val] = task_dict
                    if '-image-' in  val and  val not in baseimgs_dict.keys():
                        img_dict = {}
                        img_dict[val] = val
                        img_dict['summary'] = tree_model["pn"][val]["summary"]
                        img_dict['license'] = tree_model["pn"][val]["license"]
                        img_dict['section'] = tree_model["pn"][val]["section"]
                        baseimgs_dict[val] = img_dict
                '''
                save recipe,task,baseimage to db
                '''
                current_operator_name = request.session.get("current_operator")
                current_operator = Operator.objects.filter(username=current_operator_name)[0]
                TreeModel.objects.filter(operator=current_operator).delete()
                for key,value in recipes_dict.iteritems():
                    TreeModel(types='recipe',name=key,license=str(value['license']),group=str(value['section']),description=str(value['summary']),is_included=False,operator=current_operator).save()
                for key,value in baseimgs_dict.iteritems():
                    TreeModel(types='baseimage',name=str(key),license=str(value['license']),group=str(value['section']),description=str(value['summary']),is_included=False,operator=current_operator).save()
                for key,value in tasks_dict.iteritems():
                    TreeModel(types='task',name=str(key),license=str(value['license']),group=str(value['section']),description=str(value['summary']),is_included=False,operator=current_operator).save()
                baseimgs_list = []
                baseimgs = TreeModel.objects.filter(types='baseimage').order_by("name")
                for item in baseimgs:
                    temp_dict = {}
                    temp_dict['name']=item.name
                    temp_dict['desc']=item.description
                    baseimgs_list.append(temp_dict)
                events={'baseImgs': baseimgs_list}
            elif item['event'] == "CacheLoadProgress":
                events={'cacheProgress': 'progress', 'value': item['value']}
            elif item['event'] == "TreeDataPreparationProgress":
                events={'treedataProgress': 'progress', 'value': item['value']}
            else:
                continue
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

def recipe_task_list(request):
    baseImg_value = request.POST['radio'].strip()
    bitbake = Bitbakeserver.objects.filter(ip=request.session.get("bitbake_ip"))[0]
    BuildConfig.objects.filter(bitbakeserver=bitbake,build_result=False).update(base_image=baseImg_value)
    tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()

    tree_dict = eval(tree_str)
    tree_model = tree_dict['model']

    values_list = commons.select_base_image_dep(baseImg_value,tree_model)
    pkg_list = ''
    rcp_list = ''
    for item in values_list:
        TreeModel.objects.filter(name=str(item)).update(is_included=True)
        if 'task-' in item:
            pkg_list = pkg_list + item+' '
        else:
            rcp_list = rcp_list + item+' '
    rcp_included = TreeModel.objects.filter(types='recipe',is_included=True).count()
    task_included = TreeModel.objects.filter(types='task',is_included=True).count()
    recipes = TreeModel.objects.filter(types='recipe').order_by("name")
    rcp_total = len(recipes)
    tasks = TreeModel.objects.filter(types='task').order_by("name")
    tasks_total = len(tasks)
    included = TreeModel.objects.filter(is_included=True).order_by("name")
    included_total = len(included)
    return render_to_response('web/recipe_task_list.html',locals())

def buildPackage_request(request):
    ip = request.session.get("bitbake_ip")
    current_operator_name = request.session.get("current_operator")
    task_list = request.REQUEST.getlist('task_checkbox')
    recipe_list = request.REQUEST.getlist('recipe_checkbox')
    included_list = recipe_list + task_list
    #included_list = request.REQUEST.getlist('include_checkbox')
    str_rcplist = ' '
    for val in recipe_list:
        str_rcplist = str_rcplist+str(val)+' '
    str_tasklist = ' '
    for val in task_list:
        str_tasklist = str_tasklist + str(val) + ' '
    current_operator = Operator.objects.filter(username=current_operator_name)[0]
    BuildConfig.objects.filter(operator=current_operator,build_result=False).update(recipes=str_rcplist,recipe_total=len(recipe_list),tasks=str_tasklist,task_total=len(task_list))
    buildConfig = BuildConfig.objects.filter(operator=current_operator,build_result=False)[0]

    build_pkg = {}
    build_pkg['baseImage']=buildConfig.base_image
    build_pkg['layers']=buildConfig.layers.strip().split(' ')
    build_pkg['curr_mach']=buildConfig.machine
    build_pkg['curr_package_format']=buildConfig.package_format.split(',')
    build_pkg['curr_distro']=buildConfig.distro
    build_pkg['image_extra_size']=buildConfig.image_extra
    build_pkg['curr_sdk_machine']=buildConfig.build_toolchain
    build_pkg['bbthread']=buildConfig.bb_number_threads
    build_pkg['pmake']=buildConfig.parallel_make
    build_pkg['dldir']=buildConfig.download_directory
    build_pkg['sstatedir']=buildConfig.sstate_directory
    build_pkg['sstatemirror']=buildConfig.sstate_mirror
    build_pkg['incompat_license']=''
    build_pkg['extra_setting']=buildConfig.key_value_variable
    build_pkg['rcp_list']=included_list
    response=sendRequest(ip,settings.RESTFUL_API_BUILD_PACKAGE,build_pkg)
    status = simplejson.loads(response)
    if status['status'] == 'OK':
        return render_to_response('web/buildPackage_log.html',locals())
    else:
        error_msg =status['action']+":"+status['error_info']
        return render_to_response('error.html',locals())

def getPackage_event(request):
    queue = []
    filter_packageEvent(request,queue)
    events = {}
    build_logs = []
    if queue:
        for item in queue:
            if item['event'] == "CacheLoadProgress":
                events = {'cacheProgress': 'cacheprogress', 'value': item['value']}
            elif item['event'] == "BuildStarted":
                events = {'build_start': 'build_started', 'value': item['value']}
            elif item['event'] == "runQueueTaskStarted":
                events = {'queueProgress': 'buildprogress', 'value': item['value']}
            elif item['event'] == "TaskStarted":
                build_logs.append({'package':item['value']['package'], 'task': item['value']['task']})
                events = {'buildLogs':build_logs}
            elif item['event'] == "BuildCompleted":
                pkg_size = parse_package_tree(request)
                events = {'packageTree':'pkg_tree','selected_packageSize':pkg_size}
            elif item['event'] == "TaskFailed":
                error = item['value']['logdata']
                events = {'error':error[error.index('ERROR'):-1]}
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")
def parse_package_tree(request):
    tree_file = open (settings.TEMPLATE_PATH+"/packageTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()

    tree_list= eval(tree_str)
    current_operator_name = request.session.get("current_operator")
    current_operator = Operator.objects.filter(username=current_operator_name)[0]
    buildConfig = BuildConfig.objects.filter(operator=current_operator,build_result=False)[0]
    task_list = buildConfig.tasks.strip().split(' ')
    pkg_dependency_list = []
    for val in task_list:
        pkg_dependency_list += commons.include_pkg_child_dep(val, tree_list)
    tree_list.sort()

    pkg_size = 0
    for item in tree_list:
        TreeModel(types='package',name=str(item['package']),pkg_parent=' ',is_included=False,operator=current_operator).save()
        item['package_value'].sort()
        for val in item['package_value']:
            if str(val['pkg']) in pkg_dependency_list:
                pkg_size = pkg_size + int(val['size'])
                TreeModel(types='package',name=str(val['pkg']),group=str(val['section']),description=str(val['summary']),size=int(val['size']),pkg_parent=str(item['package']),is_included=True,operator=current_operator).save()
            else:
                TreeModel(types='package',name=str(val['pkg']),group=str(val['section']),description=str(val['summary']),size=int(val['size']),pkg_parent=str(item['package']),is_included=False,operator=current_operator).save()
    pkg_size = pkg_size/1024
    return pkg_size

def package_list(request):
    pkg_size = request.GET.get("pkgSize")
    packages = TreeModel.objects.filter(types='package').order_by("name")
    parent_packages = TreeModel.objects.filter(types='package',pkg_parent=' ').order_by("name")
    included_packages = TreeModel.objects.filter(types='package',is_included=True).order_by("name")
    packages_total = len(packages)
    included_total = len(included_packages)
    return render_to_response('web/package_list.html',locals())

def buildImage_request(request):
    ip = request.session.get("bitbake_ip")
    bitbake = Bitbakeserver.objects.filter(ip=ip)[0]
    build_config = BuildConfig.objects.filter(bitbakeserver=bitbake,build_result=False)[0]
    package_list = request.REQUEST.getlist('package_checkbox')
    selected_pkg_total = request.POST['selected_pkgTotal'].strip()
    selected_pkg_size = request.POST['selected_pkgSize'].strip()
    packages = ' '
    for val in package_list:
        packages = packages + str(val) +' '
    BuildConfig.objects.filter(bitbakeserver=bitbake,build_result=False).update(packages=packages,package_total=int(selected_pkg_total),package_size=int(selected_pkg_size))

    build_img = {}
    build_img['curr_mach'] = build_config.machine
    build_img['baseImage'] = build_config.base_image
    build_img['layers'] = build_config.layers.strip().split(" ")
    build_img['curr_package_format'] = build_config.package_format.split(",")
    build_img['curr_distro'] = build_config.distro
    build_img['image_extra_size'] = build_config.image_extra
    build_img['curr_sdk_machine'] = build_config.build_toolchain
    build_img['bbthread'] = build_config.bb_number_threads
    build_img['pmake'] = build_config.parallel_make
    build_img['dldir'] = build_config.download_directory
    build_img['sstatedir'] = build_config.sstate_directory
    build_img['sstatemirror'] = build_config.sstate_mirror
    build_img['incompat_license'] = ''
    build_img['extra_setting'] = {}
    build_img['rcp_list'] = build_config.recipes.strip().split(' ')
    build_img['pkg_list'] = package_list
    response=sendRequest(ip,settings.RESTFUL_API_BUILD_IMAGE,build_img)
    status = simplejson.loads(response)
    if status['status'] == 'OK':
        return render_to_response('web/buildImg_log.html',locals())
    else:
        error_msg =status['action']+":"+status['error_info']
        return render_to_response('error.html',locals())

def getImage_event(request):
    queue = []
    filter_imageEvent(request,queue)
    events = {}
    build_logs = []
    if queue:
        for item in queue:
            if item['event'] == "CacheLoadProgress":
                events = {'cacheProgress': 'cacheprogress', 'value': item['value']}
            elif item['event'] == "BuildStarted":
                events = {'build_start': 'build_started', 'value': item['value']}
            elif item['event'] == "runQueueTaskStarted":
                events = {'queueProgress': 'buildprogress', 'value': item['value']}
            elif item['event'] == "TaskStarted":
                build_logs.append({'package':item['value']['package'], 'task': item['value']['task']})
                events = {'buildLogs':build_logs}
            elif item['event'] == "BuildCompleted":
                events = {'buildImg_status':'ok'}
            elif item['event'] == "TaskFailed":
                error = item['value']['logdata']
                events = {'error':error[error.index('ERROR'):-1]}
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

'''
build image complete, release bitbake connection, store successful build config
into db, empty TreeModel table information
'''
def disp_image(request):
    ip = request.session.get("bitbake_ip")
    Bitbakeserver.objects.filter(ip=ip).update(status='0')
    Operator.objects.filter(bitbakeserver=Bitbakeserver.objects.filter(ip=ip)[0]).update(bitbakeserver=None)
    build_config = BuildConfig.objects.filter(bitbakeserver=Bitbakeserver.objects.filter(ip=ip)[0],build_result=False)[0]
    BuildConfig.objects.filter(bitbakeserver=Bitbakeserver.objects.filter(ip=ip)[0],build_result=False).update(build_result=True)
    TreeModel.objects.all().delete()
    return render_to_response('web/image_list.html',locals())

def get_recipe_dependency(request):
    selected_recipe = request.GET.get("selected_recipe").encode().strip()
    is_checked = request.GET.get("is_checked").encode().strip()
    tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()

    tree_dict = eval(tree_str)
    tree_model = tree_dict['model']
    recipeDependency_list = []

    if 'task-' not in selected_recipe:
        recipeDependency_list =commons.find_rcp_dep(selected_recipe, tree_model)
    else:
        recipeDependency_list.append(selected_recipe)

    if is_checked =='0':
        TreeModel.objects.filter(name__in=recipeDependency_list).update(is_included=False)
    else:
        TreeModel.objects.filter(name__in=recipeDependency_list).update(is_included=True)
    return HttpResponseRedirect('/hob/disp_recipes_tasks/')

def disp_recipes_tasks(request):
    rcp_included = TreeModel.objects.filter(types='recipe',is_included=True).count()
    task_included = TreeModel.objects.filter(types='task',is_included=True).count()
    recipes = TreeModel.objects.filter(types='recipe').order_by("name")
    rcp_total = len(recipes)
    tasks = TreeModel.objects.filter(types='task').order_by("name")
    tasks_total = len(tasks)
    included = TreeModel.objects.filter(is_included=True).order_by("name")
    included_total = len(included)
    return render_to_response('web/recipe_task_list.html',locals())

def get_package_dependency(request):
    selected_package = request.GET.get("selected_package").encode().strip()
    is_child = request.GET.get("is_child").encode().strip()
    is_checked = request.GET.get("is_checked").encode().strip()
    tree_file = open (settings.TEMPLATE_PATH+"/packageTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_list= eval(tree_str)

    packageDependency_list = []
    if is_child == "0":
        packageDependency_list = commons.include_pkg_parent_dep(selected_package, tree_list)
    else:
        packageDependency_list = commons.include_pkg_child_dep(selected_package, tree_list)
    if is_checked == '0':
        TreeModel.objects.filter(name__in=packageDependency_list).update(is_included=False)
    else:
        TreeModel.objects.filter(name__in=packageDependency_list).update(is_included=True)
    return HttpResponseRedirect('/hob/disp_packages/')

def disp_packages(request):
    packages = TreeModel.objects.filter(types='package').order_by("name")
    parent_packages = TreeModel.objects.filter(types='package',pkg_parent=' ').order_by("name")
    included_packages = TreeModel.objects.filter(types='package',is_included=True).order_by("name")
    packages_total = len(packages)
    included_total = len(included_packages)
    pkg_size = 0
    for item in packages:
        if item.is_included == True  :
            pkg_size += item.size
    pkg_size = pkg_size/1024
    return render_to_response('web/package_list.html',locals())

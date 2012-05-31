'''
Created on 2012-5-25
@author: lvchunhX
'''
from hob.models import BuildConfig, TreeModel
from utils.commond import sendRequest
import settings,simplejson,time
from django.http import HttpResponse
from django.shortcuts import render_to_response
from management.filterEvent import FilterEvent
from management.models import Operator
from utils import pkg_dep_include
from utils.storePackageTreeData import StorePackageDataToDB
from django.http import HttpResponseRedirect

queue = []
def buildPackage_request(request):
    current_user = request.session.get("username")
    bitbake = request.session.get("bitbake")
    recipes = None
    tasks = None
    if request.method=="POST":
        recipes = request.POST.getlist('recipe_checkbox')
        tasks = request.POST.getlist('task_checkbox')
        recipes.extend(tasks)
    else:
        recipes = TreeModel.objects.filter(operator__username=current_user, types='recipe', is_included=True)
        tasks = TreeModel.objects.filter(operator__username=current_user, types='task', is_included=True)
        recipes.extend(tasks)

    rcp_str = ' '
    for val in recipes:
        rcp_str = rcp_str + str(val) +' '
    task_str = ' '
    for val in tasks:
        task_str = task_str + str(val) +' '
    buildConfig = BuildConfig.objects.filter(operator__username=current_user, build_result=False)[0]
    buildConfig.recipes = rcp_str
    buildConfig.recipe_total = len(recipes)
    buildConfig.tasks = task_str
    buildConfig.task_total = len(tasks)
    buildConfig.save()

    build_pkg = {}
    build_pkg['baseImage']=buildConfig.base_image
    build_pkg['layers']=buildConfig.layers.strip().split(' ')
    build_pkg['curr_mach']=buildConfig.machine
    build_pkg['curr_package_format']=buildConfig.package_format
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
    build_pkg['rcp_list']=recipes

    response=sendRequest(bitbake.ip, bitbake.port, settings.RESTFUL_API_BUILD_PACKAGE, build_pkg)
    status = simplejson.loads(response)
    if status['status'] == 'OK':
        TreeModel.objects.filter(types='package', operator__username=current_user).delete()
        FilterEvent(bitbake.ip, bitbake.port, queue, 'package').handle_event()
    return render_to_response('web/package_build.html',locals())

def getPackage_event(request):
    events = {}
    log_queue = []
    progress_rate = None

    if queue:
        for item in queue:
            if item['event'] == "runQueueTaskStarted":
                progress_rate = int(item['value']['num_of_completed']*100.0/item['value']['total'])
                events['building'] = progress_rate
            elif item['event'] == "LogRecord":
                if 'OE Build' in item['value']:
                    events['buildConfig'] = item['value']
                else:
                    events['logs'] = item['value']
            elif item['event'] == "BuildStarted":
                events['buildStart'] = item['value']
            elif item['event'] == "TaskStarted":
                log_queue.append({'package':item['value']['package'], 'task': item['value']['task']})
                events['tasklog'] = log_queue
            elif item['event'] == "BuildCompleted":
                parse_package_tree(request)
            elif item['event'] == "TaskFailed":
                error = item['value']['logdata']
                events['error'] = error[error.index('ERROR'):-1]
            elif item['event'] == "CommandCompleted":
                events = {'packageTree':'pkg_tree'}
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

def parse_package_tree(request):
    tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_dict = eval(tree_str)

    tree_file = open (settings.TEMPLATE_PATH+"/packageTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_list= eval(tree_str)

    buildConfig = BuildConfig.objects.filter(operator__username=request.session.get("username"), build_result=False)[0]
    pkg_list = tree_dict['model']["rdepends-pn"].get(buildConfig.base_image, [])
    pkg_dependency_list = []
    package_str = ' '
    for val in pkg_list:
        pkg_dependency_list += pkg_dep_include.include_pkg_child_dep(str(val), tree_list)
    for val in pkg_dependency_list:
        package_str = package_str + str(val) +' '
    buildConfig.packages = package_str
    buildConfig.save()

    tree_list.sort()
    current_operator = Operator.objects.filter(username=request.session.get("username"))[0]
    StorePackageDataToDB(pkg_dependency_list, tree_list, current_operator).start()

def package_list(request):
    buildconfig = BuildConfig.objects.filter(operator__username=request.session.get("username"))[0]
    pkg_size = buildconfig.package_size
    while pkg_size is None:
        time.sleep(60)
    packages = TreeModel.objects.filter(types='package').order_by("name")
    parent_packages = TreeModel.objects.filter(types='package',pkg_parent=' ').order_by("name")
    included_packages = TreeModel.objects.filter(types='package',is_included=True).order_by("name")
    return render_to_response('web/package_list.html',locals())

def get_package_dependency(request):
    selected_package = request.GET.get("selected_package").encode().strip()
    is_checked = request.GET.get("is_checked").encode().strip()

    tree_file = open (settings.TEMPLATE_PATH+"/packageTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_list= eval(tree_str)
    packageDependency_list = pkg_dep_include.include_pkg_child_dep(selected_package, tree_list)

    if is_checked == '0':
        TreeModel.objects.filter(name__in=packageDependency_list).update(is_included=False)
    else:
        TreeModel.objects.filter(name__in=packageDependency_list).update(is_included=True)

    package_size = 0
    package_selected = TreeModel.objects.filter(operator__username=request.session.get("username"), is_included=True)
    for val in package_selected:
        if val.size:
            package_size += val.size
    package_size = package_size/1024
    BuildConfig.objects.filter(operator__username=request.session.get("username"), build_result=False).update(package_size=package_size)
    return HttpResponseRedirect('/hob/package_list/')
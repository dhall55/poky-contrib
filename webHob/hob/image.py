'''
Created on 2012-5-29
@author: lvchunhX
'''
from hob.models import BuildConfig
import settings,simplejson
from utils.commond import sendRequest
from management.filterEvent import FilterEvent
from django.shortcuts import render_to_response
from django.http import HttpResponse
from management.models import Bitbakeserver, Operator

queue = []
def buildImage_request(request):
    buildConfig = BuildConfig.objects.filter(operator__username=request.session.get("username"))[0]
    bitbake = request.session.get("bitbake")
    package_list = []
    if request.method=="POST":
        package_list = request.POST.getlist('package_checkbox')
        package_str = ' '
        for val in package_list:
            package_str = package_str + val + " "
        buildConfig.packages = package_str
        buildConfig.package_total = len(package_list)
        buildConfig.save()
    else:
        package_list = buildConfig.packages.strip().split(" ")

    recipes = buildConfig.recipes.strip().split(' ')

    build_img = {}
    build_img['curr_mach'] = buildConfig.machine
    build_img['baseImage'] = buildConfig.base_image
    build_img['layers'] = buildConfig.layers.strip().split(" ")
    build_img['curr_package_format'] = buildConfig.package_format.split(",")
    build_img['curr_distro'] = buildConfig.distro
    build_img['image_extra_size'] = buildConfig.image_extra
    build_img['curr_sdk_machine'] = buildConfig.build_toolchain
    build_img['bbthread'] = buildConfig.bb_number_threads
    build_img['pmake'] = buildConfig.parallel_make
    build_img['dldir'] = buildConfig.download_directory
    build_img['sstatedir'] = buildConfig.sstate_directory
    build_img['sstatemirror'] = buildConfig.sstate_mirror
    build_img['incompat_license'] = ''
    build_img['extra_setting'] = {}
    build_img['rcp_list'] =  recipes
    build_img['pkg_list'] = package_list
    build_img['fast_mode'] = True

    response=sendRequest(bitbake.ip, bitbake.port, settings.RESTFUL_API_BUILD_IMAGE, build_img)
    status = simplejson.loads(response)

    if status['status'] == 'OK':
        FilterEvent(bitbake.ip, bitbake.port, queue, 'image').handle_event()
    return render_to_response('web/image_build.html',locals())

def getImage_event(request):
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
                events = {'buildImage':'successful'}
            elif item['event'] == "TaskFailed":
                error = item['value']['logdata']
                events['error'] = error[error.index('ERROR'):-1]
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

def disp_image(request):
    buildConfig = BuildConfig.objects.filter(operator__username=request.session.get("username"), build_result=False)[0]
    buildConfig.build_result = True
    buildConfig.image_size = buildConfig.package_size
    buildConfig.save()
    bitbake = request.session.get("bitbake")
    Bitbakeserver.objects.filter(name=bitbake.name).update(status=0)
    Operator.objects.filter(username=request.session.get("username")).update(status=0, bitbakeserver =None)

    recipes = buildConfig.recipes.strip().split(" ")
    packages = buildConfig.packages.strip().split(" ")
    return render_to_response('web/image_list.html',locals())
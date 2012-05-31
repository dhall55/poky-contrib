'''
Created on 2012-5-21
@author: lvchunhx
'''
from utils.commond import getEvent
import settings,simplejson
from django.shortcuts import render_to_response
from hob.models import BuildConfig, SystemConfig
from management.models import Operator
from django.http import HttpResponseRedirect,HttpResponse
from urllib2 import URLError
import types
from hob.forms import advanceSettingForm

def index(request):
    bitbake = request.session.get("bitbake")
    operator = Operator.objects.filter(username=request.session.get("username"))

    if BuildConfig.objects.filter(operator__id__exact=operator[0].id, build_result=False):
        pass
    else:
        try:
            str_packagingformat = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_PACKING_FORMAT)
            packagingformat = eval(str_packagingformat)['PACKAGE_CLASSES'].lstrip('package_')

            str_imageRootfs = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_IMAGE_ROOTFS_SIZE)
            imageRootfs = eval(str_imageRootfs)['IMAGE_ROOTFS_EXTRA_SPACE'].strip()

            str_buildToolchain = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_BUILD_TOOLCHAIN)
            buildToolchain = eval(str_buildToolchain)['SDK_ARCH']

            str_distro = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_DISTRO)
            distro = eval(str_distro)['DISTRO']

            str_bbNumberThread = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_BB_NUMBER_THREADS)
            bbNumberThread = eval(str_bbNumberThread)['BB_NUMBER_THREADS']
            if bbNumberThread == '':
                numberThreads = eval(getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_NUMBER_THREADS))['getCpuCount']
                if numberThreads:
                    bbNumberThread = numberThreads
                else:
                    bbNumberThread = 4

            str_parallelMake = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_PARALLEL_MAKE)
            parallelMake = eval(str_parallelMake)['PARALLEL_MAKE']
            if parallelMake == '':
                parallelMake = 4
            elif '-j' in parallelMake:
                parallelMake = parallelMake.strip('-j ')

            str_downloadDir = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_DOWNLOAD_DIRECTORY)
            downloadDir = eval(str_downloadDir)['DL_DIR'].strip()

            str_sstateDir = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_SSTATE_DIRECTORY)
            sstateDir = eval(str_sstateDir)['SSTATE_DIR'].strip()

            str_sstateMirror = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_SSTATE_MIRROR)
            sstateMirror = eval(str_sstateMirror)['SSTATE_MIRROR'].strip()

            str_layers = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_LAYERS)
            layers = eval(str_layers)['BBLAYERS'].strip()

            BuildConfig(operator=operator[0],
                                bitbakeserver=bitbake,
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
            request.session["error_msg"] = " connection is error !"
            return HttpResponseRedirect('/error/')
    return render_to_response('web/index.html',locals())

def buildConfig_request(request):
    bitbake = request.session.get("bitbake")
    response = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_SYSTEM_CONFIG_REQUEST)
    return HttpResponse(response)

def get_configEvents(request):
    bitbake = request.session.get("bitbake")
    response = getEvent(bitbake.ip, bitbake.port, settings.RESTFUL_API_EVENT_QUEUE)
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
        elif item['event'] == 'CommandCompleted':
            config_dict['action'] = 'OK'
    return HttpResponse(content=simplejson.dumps(config_dict), mimetype="text/plain")

def disp_advanceSettings(request):
    system_configs = SystemConfig.objects.filter(types__in=['formats','distros','machines-sdk']).order_by("name")
    current_config = BuildConfig.objects.filter(operator__username=request.session.get("username"))[0]
    img_types = []
    if current_config.image_type:
        img_types = current_config.image_type.strip().split(" ")
    return render_to_response('web/advanceSettings.html',locals())

def save_advanceSetting(request):
    imgTypes = ''
    if request.POST.getlist('imgTypes'):
        for val in request.POST.getlist('imgTypes'):
            imgTypes = imgTypes + str(val) + ' '

    pkg_formats = ''
    if request.POST.getlist('package_format'):
        for val in request.POST.getlist('package_format'):
            pkg_formats = pkg_formats + str(val) + ' '

    form = advanceSettingForm(request.POST)
    if form.is_valid():
        BuildConfig.objects.filter(operator__username=request.session.get("username")) \
                            .update(image_type = imgTypes, package_format = pkg_formats, \
                                    image_rootfs = form.data['image_rootfs'], \
                                    image_extra = form.data['image_extra'], \
                                    build_toolchain = form.data['build_toolchain'], \
                                    distro = form.data['distro'], \
                                    bb_number_threads = form.data['bb_number_threads'], \
                                    parallel_make = form.data['parallel_make'], \
                                    download_directory = form.data['download_directory'], \
                                    sstate_directory = form.data['sstate_directory'], \
                                    sstate_mirror = form.data['sstate_mirror'])
    return HttpResponseRedirect('/hob/index/')
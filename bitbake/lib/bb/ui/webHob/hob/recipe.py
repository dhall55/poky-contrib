'''
Created on 2012-5-22
@author: lvchunhx
'''
from hob.models import BuildConfig, TreeModel
from utils.commond import sendRequest
import simplejson,settings
from django.http import HttpResponse
from management.filterEvent import FilterEvent
from management.models import Operator
from utils.util import storeTreeDataToDB

queue = []
def parseRecipe_request(request):
    machine = request.POST['machine']
    bitbake = request.session.get("bitbake")
    config = BuildConfig.objects.filter(bitbakeserver__id = bitbake.id, build_result=False)[0]
    config.machine = machine
    config.save()

    build_config = {}
    build_config['layers'] = config.layers.split(' ')
    build_config['curr_mach'] = machine
    build_config['curr_package_format'] = config.package_format.split(',')
    build_config['curr_distro'] = config.distro
    build_config['imageRoot'] = config.image_rootfs
    build_config['image_extra_size'] = config.image_extra
    build_config['curr_sdk_machine'] = config.build_toolchain
    build_config['bbthread'] = config.bb_number_threads
    build_config['pmake'] = config.parallel_make
    build_config['dldir'] = config.download_directory
    build_config['sstatedir'] = config.sstate_directory
    build_config['sstatemirror'] = config.sstate_mirror
    build_config['incompat_license'] = ''
    build_config['extra_setting'] = {}

    response=sendRequest(bitbake.ip, bitbake.port, settings.RESTFUL_API_PARSE_RECIPE, build_config)
    status = simplejson.loads(response)
    if status['status'] == 'OK':
        FilterEvent(bitbake.ip, bitbake.port, queue, 'recipe').handle_event()
    return HttpResponse(content=simplejson.dumps(status), mimetype="text/plain")

def parseRecipe_event(request):
    current_operator = Operator.objects.filter(username=request.session.get("username"))[0]
    TreeModel.objects.filter(operator__username=current_operator.username).delete()
    events = {}
    recipes_dict = {}
    baseimgs_list = []
    tasks_dict = {}
    progress_rate = None
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
                    if '-image' in  val and  val not in baseimgs_list:
                        baseimgs_list.append(val)
                baseimgs_list.sort()
                storeTreeDataToDB(recipes_dict, 'recipe', current_operator).start()
                storeTreeDataToDB(baseimgs_list, 'baseimage', current_operator).start()
                storeTreeDataToDB(tasks_dict, 'task', current_operator).start()
                events={'baseImages': baseimgs_list}
            else:
                if item['event'].endswith('Started'):
                    if item['event'] == "TreeDataPreparationStarted":
                        progress_rate = 60
                    else:
                        progress_rate = 0
                elif item['event'].endswith('Progress'):
                    if item['event'] == "TreeDataPreparationProgress":
                        progress_rate = 60 + int(item['value']['current']*40.0/item['value']['total'])
                    else:
                        progress_rate = int(item['value']['current']*60.0/item['value']['total'])
                elif item['event'].endswith('Completed'):
                    if item['event'] == "TreeDataPreparationCompleted":
                        progress_rate = 100
                    else:
                        progress_rate = 60
                events={'status':'parsing', 'value': progress_rate}
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")
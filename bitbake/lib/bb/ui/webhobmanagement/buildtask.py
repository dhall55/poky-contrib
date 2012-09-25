import threading,time
from webhobhandler import WebhobHandler
from wsconnection import Connection

class BuildTask:
    (INITIALIZE, CONFIGURATION, RECIPES, PACKAGES, IMAGE, PACKAGEINFO, SANITY_CHECK) = range(7)
    def __init__(self, guid, interface, recipe_model=None, pkgs_model=None):
        self.wsserver = Connection("http://%s:%s/?wsdl" % interface)
        self.interface = interface
        self.handler = WebhobHandler(self.wsserver)
        self.info = {}
        self.guid = guid
        self.ret_value = {}
        self.process_value = {}
        self.error_msg = ''
        self.recipe_model = recipe_model
        self.pkgs_model = pkgs_model
        self.fast_build_params = None
#        self.fast_mode = False
        self.fast_mode_step=0

    def initialize_new_build(self):
        self.handler.initialize_configuration()
        return 'ok'

    def get_image_info(self,image_name, curr_mach, image_types):
        return self.wsserver.get_images(image_name, curr_mach, image_types)

    def generate_configuration(self, params):
        self.set_user_config(params)
        self.handler.generate_configuration()
        return 'ok'

    def generate_recipes(self, params):
        self.set_user_config(params)
#        self.handler.init_cooker()
        self.handler.generate_recipes()
        return 'ok'

    def generate_packages(self, params):
        self.set_user_config(params)
#        print params
        if params.get('selected_recipes', None) is None:
            return 'Faild: selected recipe is empyty, cannot build package'

        self.handler.generate_packages(params['selected_recipes'], "build")
        return 'ok'

    def fast_build_image(self, params):
        self.set_user_config(params)
        if params.get('selected_recipes', None) is None:
#            print 'Faild: selected recipe is empty, cannot build package'
            return 'Faild: selected recipe is empty, cannot build package'

        self.fast_build_params = params
#        print params
#        self.fast_mode = True
        self.fast_mode_step = 1
        self.handler.generate_packages(params['selected_recipes'], "build")
        return 'ok'

    def generate_image(self, params):
        if self.fast_mode_step:
            self.fast_mode_step = 2
        self.set_user_config(params)
        image = ''
#        self.handler.generate_image(image, [], image_packages=[], toolchain_packages=[], default_task="build")

        toolchain_packages = []
        hob_toolchain = "hob-toolchain"
        if params.get('toolchain_build', None):
            toolchain_packages = params['toolchain_build']

        if params.get('is_base_image', None) == 0:
            packages = params.get('selected_packages', None)
            image = 'hob_image'
        else:
            packages = []
            image = params.get('selected_image', None)
        self.handler.generate_image(image,
                                    hob_toolchain,
                                    packages,
                                    toolchain_packages,
                                    "build")

        return 'ok'
#    def cancel_parse(self):
#        pass

    def cancel_build(self, is_force_cancel):
        if is_force_cancel == 'true':
            force = True
        elif is_force_cancel == 'false':
            force = False
        else:
            return 'param error'
        self.handler.cancel_build(force)
        return 'ok'

    def process_results_clear(self):
        self.ret_value = {}
        self.process_value = {}

    def polling_event(self, cmd_request):
        if cmd_request in ('parse_configuration', 'initialize_new_build'):
            return self.configuration_eventhandler()
        elif cmd_request == 'parse_recipe':
            return self.recipe_eventhandler()
        elif cmd_request == 'build_package' or cmd_request == 'build_image':
            return self.building_eventhandler()
        elif cmd_request == 'fast_build_image':
            return self.fast_image_building_eventhandler()
        elif cmd_request == 'cancel_build':
            return self.cancel_event()

    def configuration_eventhandler(self):
        event=self.handler.getEvents()
        if self.handler.action == self.INITIALIZE or self.handler.action == self.CONFIGURATION:
            if isinstance(event, list):
                for item in event:
                    if item['event'] == 'ConfigFilesFound':
                        if item['variable'] == 'distro':
                            values = item['values'].split()
                            values.sort()
                            self.ret_value['distros'] = values
                        elif item['variable'] == 'machine':
                            values = item['values'].split()
                            values.sort()
                            self.ret_value['machines'] = values
                        elif item['variable'] == 'machine-sdk':
                            values = item['values'].split()
                            values.sort()
                            self.ret_value['machine_sdks'] = values
                    elif item['event'] == 'FilesMatchingFound':
                        if item['pattern'] == "rootfs_":
                            formats = []
                            for match in item['matches'].split():
                                classname, sep, cls = match.rpartition(".")
                                fs, sep, format = classname.rpartition("_")
                                formats.append(format)
                            formats.sort()
                            self.ret_value['formats'] = formats
                    elif item['event'] == 'LogRecord':
                        if item['levelno'] >= item['logging_ERROR']:
                            self.error_msg += item['msg'] + '\n'
                    elif item['event'] == 'Done':
                        if item['result'] == 'successed':
                            self.handler.trigger_sanity_check()
                        elif item['result'] == 'failed':
                            self.ret_value['done'] = 'Failed_done'
                            self.ret_value['error_msg'] = self.error_msg
        elif self.handler.action == self.SANITY_CHECK:
            if isinstance(event, list):
                for item in event:
                    if item['event'] == 'SanityCheckFailed':
                        self.ret_value['sanity_check_failed'] = item["msg"]
                    elif item['event'] == 'SanityCheck':
                        self.ret_value['done'] = 'Successed_done'
                        self.ret_value['parameters'] = self.handler.get_parameters()

        if self.ret_value.get('done', None):
            return self.ret_value
        else:
            return {'status':'handling'}

    def recipe_eventhandler(self):
        event=self.handler.getEvents()
#        if isinstance(event, list):
#            for item in event:
#                if item['event'] == 'LogRecord':
#                    continue
#                print item['event']
        if self.handler.action == self.RECIPES:
            if isinstance(event, list):
                for item in event:
                    if item['event'] in ('ParseStarted',
                                        'CacheLoadStarted',
                                        'TreeDataPreparationStarted'):
                        if item['event'] == 'TreeDataPreparationStarted':
                            pct = 60
                        else:
                            pct = 0
                        self.process_value['pct'] = pct
                    elif item['event'] in ('ParseProgress',
                                           'CacheLoadProgress',
                                           'TreeDataPreparationProgress'):
                        fraction = item["current"] * 100.0/item["total"]
                        if item['event'] == 'TreeDataPreparationProgress':
                            pct= 60 + int(fraction*0.3)
                        else:
                            pct = int(0.6 * fraction)
                        self.process_value['pct'] = pct
                    elif item['event'] == "TargetsTreeGenerated":
    #                    data = item["model"]
    #                    model = RecipeModel.objects
    #                    model.populate(data)
                        pct = 95
                        self.process_value['pct'] = pct
                        self.ret_value['model'] = item["model"]
#                        if item["model"]:
#                            self.ret_value['model'] = self.recipe_model.populate(item["model"])
                    elif item['event'] == 'LogRecord':
                        if item['levelno'] >= item['logging_ERROR']:
                            self.error_msg += item['msg'] + '\n'
                    elif item['event'] == 'Done':
                        if item['result'] == 'successed':
                            self.handler.request_package_info()
                        elif item['result'] == 'failed':
                            self.ret_value['done'] = 'Failed_done'
                            self.ret_value['error_msg'] = self.error_msg
        elif self.handler.action == self.PACKAGEINFO:
            if isinstance(event, list):
                for item in event:
                    if item['event'] == 'PackageInfo':
                        self.ret_value['pkginfolist'] = item["pkginfolist"]
                        self.ret_value['done'] = 'Successed_done'

        if self.ret_value.get('done', None):
            return self.ret_value
        else:
            self.process_value['status']='handling'
            return self.process_value

    def building_eventhandler(self):
        ret = {}
#        pct = 0
        event = self.handler.getEvents()
        if self.handler.action == self.PACKAGES or self.handler.action == self.IMAGE:
            if isinstance(event, list):
                for item in event:
    #                if db_status.action == constant.GENERATE_PACKAGES or db_status.action == constant.GENERATE_IMAGE:
                        if item['event'] in ('ParseStarted','CacheLoadStarted'):
                            pct = 0
                            ret['pct'] = pct
                        elif item['event'] in ('ParseProgress','CacheLoadProgress'):
                            pct = int(item["current"]*20.0/item["total"])
                            ret['pct'] = pct
                        elif item['event'] in ('ParseCompleted','CacheLoadCompleted'):
                            pct = 20
                            ret['pct'] = pct
                        elif item['event'] in ('TaskStarted','TaskBase','TaskSucceeded'):
                            message = {'event':item['event'],
                                       'package':item['package'],
                                       'task':item['task'],
                                       'message':item['message'],
                                       'pid':item['pid'],
                            }
                            ret['task'] = message
                        elif item['event'] == 'runQueueTaskCompleted':
                            message = {'event':item['event'],
                                       'taskstring':item['taskstring'],
                                       'pid':item['pid'],
                                       'taskid':item['taskid'],
                            }
                            ret['taskcompleted'] = message
                        elif item['event'] in ('runQueueTaskFailed','sceneQueueTaskFailed'):
                            message = {'event':item['event'],
                                       'taskid':item['taskid'],
                                       'exitcode':item['exitcode'],
                                       'taskstring':item['taskstring'],
                                       'pid':item['pid'],
                            }
                            ret['queuetaskfailed'] = message
                        elif item['event'] == 'TaskFailed':
                            message = {'event':item['event'],
                                       "logfile":item["logfile"],
                            }
                            ret['taskfailed'] = message
                        elif item['event'] == 'LogRecord':
            #                print 'msg---------',item["msg"], 'getMessage---------',item["getMessage"]
                            if 'Build Configuration' in item["msg"]:

                                message = {'event':item['event'],
                                           "conf":item["msg"]}
                                ret['build_configuration'] = message
                            if item['levelno'] >= item['logging_ERROR']:
                                message = {'event':item['event'],
                                           "error":item["msg"]}
                                ret['log_error'] = message
                        elif item['event'] == 'CommandFailed':
                            message = {'event':item['event'],
                                       "error":item["error"],
                            }
                            ret['command_failed'] = message
                        elif item['event'] == 'BuildStarted':
                            message = {'event':item['event'],
                                       'msg':"Build Started (%s)" % time.strftime('%m/%d/%Y %H:%M:%S'),
                            }
                            ret['buildstarted'] = message
                        elif item['event'] == 'BuildCompleted':
                            failures = int (item['failures'])
                            result = 0# failded =0;sucess =1
                            if (failures >= 1):
                                result = 0
                            else:
                                result = 1
                            message = {'event':item['event'],
                                       'msg':"Build Completed (%s)" % time.strftime('%m/%d/%Y %H:%M:%S'),
                                       'result':result,
                            }
                            ret['buildcompleted'] = message

                        elif item['event'] in ('runQueueTaskStarted','sceneQueueTaskStarted'):
                            num_of_completed = item['stats']['completed'] + item['stats']['failed']
                            fraction = num_of_completed * 1.0/item['stats']['total']
                            if item["event"] == "sceneQueueTaskStarted":
                                fraction = 0.2 * fraction
                            elif item["event"] == "runQueueTaskStarted":
                                fraction = 0.2 + 0.8 * fraction
                            pct = int(fraction*100)
#                            message = {'event':item['event'],
#                                       'fraction':fraction,
#                                       'current':num_of_completed,
#                                       'total':item['stats']['total'],
#                                       'taskstring':item['taskstring'],
#                            }
                            ret['pct'] = pct
                        elif item['event'] == 'NoProvider':
                            msg = ""
                            if item['runtime']:
                                r = "R"
                            else:
                                r = ""
                            if item['dependees']:
                                msg = "Nothing %sPROVIDES '%s' (but %s %sDEPENDS on or otherwise requires it)\n" % (r, item['item'], ", ".join(item['dependees']), r)
                            else:
                                msg = "Nothing %sPROVIDES '%s'\n" % (r, item['item'])
                            if item['reasons']:
                                for reason in item['reasons']:
                                    msg += ("%s\n" % reason)
                            message = {'event':'NoProvider',
                                       'msg':msg
                            }
                            ret['no_provider'] = message
                        elif item['event'] == 'Done':
                            if item['result'] == 'successed':
                                self.handler.request_package_info()
                            elif item['result'] == 'failed':
                                self.ret_value['done'] = 'Failed_done'
                                self.ret_value['error_msg'] = self.error_msg
        elif self.handler.action == self.PACKAGEINFO:
            if isinstance(event, list):
                for item in event:
                    if item['event'] == 'PackageInfo':
                        pkginfolist = item["pkginfolist"]
                        self.ret_value['pkginfolist'] = pkginfolist
                        if self.fast_mode_step ==1:
                            self.ret_value['fast_mode_build_step']='build_package_completed'
                        elif self.fast_mode_step ==2:
                            self.ret_value['fast_mode_build_step']='build_image_completed'
                            self.fast_mode_step = 0
                        self.ret_value['done'] = 'Successed_done'

        if self.ret_value.get('done', None):
            return self.ret_value
        else:
            self.process_value = ret
            self.process_value['status']='handling'
            return self.process_value
#        return {'event':self.process_value}

    def fast_image_building_eventhandler(self):
        ret = self.building_eventhandler()
        if self.fast_mode_step ==1:
            if ret.get('done', None) == 'Successed_done':
                self.generate_image(self.fast_build_params)
                del ret['done']
#                self.fast_mode = False
        return ret

    def cancel_event(self):
        event = self.handler.getEvents()
        if isinstance(event, list):
            for item in event:
                if item['event'] == 'CommandCompleted':
                    self.ret_value['done'] = 'Successed_done'

        if self.ret_value.get('done', None):
            return self.ret_value
        else:
            self.process_value['status']='handling'
            return self.process_value

    def set_user_config(self, params):
        self.handler.init_cooker()
        if params.get('layers', None):
            self.handler.set_bblayers(params['layers'])
        if params.get('machine', None):
            self.handler.set_machine(params['machine'])
        if params.get('package_format', None):
            self.handler.set_package_format(params['package_format'])
        if params.get('distro', None):
            self.handler.set_distro(params['distro'])
        if params.get('dldir', None):
            self.handler.set_dl_dir(params['dldir'])
        if params.get('sstatedir', None):
            self.handler.set_sstate_dir(params['sstatedir'])
        if params.get('sstatemirror', None):
            self.handler.set_sstate_mirror(params['sstatemirror'])
        if params.get('pmake', None):
            self.handler.set_pmake(params['pmake'])
        if params.get('bbthread', None):
            self.handler.set_bbthreads(str(params['bbthread']))
        if params.get('image_rootfs_size', None):
            self.handler.set_rootfs_size(params['image_rootfs_size'])
        if params.get('image_extra_size', None):
            self.handler.set_extra_size(params['image_extra_size'])
        if params.get('incompat_license', None):
            self.handler.handler.set_incompatible_license(params['incompat_license'])
        if params.get('sdk_machine', None):
            self.handler.set_sdk_machine(params['sdk_machine'])
        if params.get('image_fstypes', None):
            self.handler.set_image_fstypes(params['image_fstypes'])
        if params.get('extra_setting', None):
            self.handler.set_extra_config(params['extra_setting'])

        self.handler.set_extra_inherit("packageinfo")
        self.handler.set_extra_inherit("image_types")

#if initcmd == self.handler.GENERATE_CONFIGURATION:
#    self.update_configuration_parameters(self.get_parameters_sync())
#    self.sanity_check()
#elif initcmd == self.handler.SANITY_CHECK:
#    self.image_configuration_page.switch_machine_combo()
#elif initcmd in [self.handler.GENERATE_RECIPES,
#                 self.handler.GENERATE_PACKAGES,
#                 self.handler.GENERATE_IMAGE]:
#    self.update_configuration_parameters(self.get_parameters_sync())
#    self.request_package_info_async()
#elif initcmd == self.handler.POPULATE_PACKAGEINFO:
#    if self.current_step == self.RCPPKGINFO_POPULATING:
#        self.switch_page(self.RCPPKGINFO_POPULATED)
#        self.rcppkglist_populated()
#        return
#
#    self.rcppkglist_populated()
#    if self.current_step == self.FAST_IMAGE_GENERATING:
#        self.generate_image_async()

if __name__ == '__main__':
    import time
    buildtask = BuildTask('111w21312',('127.0.0.1',8889))
    import pprint
    pprint.pprint(buildtask.get_image_info('core-image-minimal', 'qemux86', 'ext3 tar.bz2'))

    #guid = '12sffasdf'
    #buildtask.initialize_new_build(guid)
    #while True:
    #    time.sleep(1)
    #    print buildtask.configuration_eventhandler(guid)

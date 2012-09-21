from hob.utils.quartz import Quartz
from hob.utils.xmlrpc_client import XmlrpcServer
import time
from hob.projects.models import Settings, Project, Layers, UserSettings
from hob.operators.models import Operator
from hob.recipe.models import RecipeModel
from hob.package.models import PackageModel
from hob.builds.models import Building, Builds, Images
from hob.utils.utils import _string_to_size
'''
HobEvents is mainly used to help django to obtain config/recipe/package/image
events from management, these events are stored in queue for django to acquire.
'''
class HobEvents:

    def __init__(self, xmlrpc_server, userName, projectName, currentWorkTask, guid, queue=None):
        self.userName = userName
        self.projectName = projectName
        self.currentWorkTask = currentWorkTask
        self.guid = guid
        self.xmlRpc = xmlrpc_server
        self.queue = queue

    def handle_event(self):
        if self.currentWorkTask =='recipe':
            self.recipe_quartz = Quartz(0.8, self.recipe_events)
            self.recipe_quartz.start()
        elif self.currentWorkTask =='package':
            self.package_quartz = Quartz(0.8, self.package_events)
            self.package_quartz.start()
        elif self.currentWorkTask =='image':
            self.image_quartz = Quartz(0.8, self.image_events)
            self.image_quartz.start()
        elif self.currentWorkTask =='settings':
            self.config_quartz = Quartz(1.0, self.get_settings_config)
            self.config_quartz.start()
        elif self.currentWorkTask == 'package_image':
            self.package_image_quartz = Quartz(0.8, self.package_image_events)
            self.package_image_quartz.start()

    def get_settings_config(self):
        value_dict = self.xmlRpc.get_events()
        if isinstance(value_dict, dict) and value_dict.has_key("done"):
            self.config_quartz.cancel()
            if "Failed" in value_dict['done']:
                setting = Settings.objects.get(project__name=self.projectName)
                setting.machine_list = setting.note
                setting.note = value_dict['error_msg']
                setting.save()
            else:
                #store settings to DB
                if len(Settings.objects.filter(project__name=self.projectName))==0:
                    setting = Settings.objects.create(project=Project.objects.get(name=self.projectName), creator=Operator.objects.get(name=self.userName))
                    UserSettings.objects.create(guid=self.guid, settings=setting, operator=Operator.objects.get(name=self.userName))
                else:
                    setting = Settings.objects.get(project__name=self.projectName)
                setting.image_rootfs_size=value_dict["parameters"]["image_rootfs_size"]
                setting.image_extra_size=value_dict["parameters"]["image_extra_size"]
                setting.build_toolchain_value=value_dict["parameters"]["sdk_machine"]
                setting.distro=value_dict["parameters"]["distro"]
                setting.image_types=value_dict["parameters"]["image_fstypes"]
                setting.package_formats=value_dict["parameters"]["pclass"].strip("package_")
                setting.gplv3_checkbox=value_dict["parameters"]["incompat_license"]
                setting.max_threads=value_dict["parameters"]["max_threads"]
                setting.parellel_make=value_dict["parameters"]["pmake"].strip("-j ")
                setting.bb_number_threads=value_dict["parameters"]["bbthread"]
                setting.download_directory=value_dict["parameters"]["dldir"]
                setting.sstate_directory=value_dict["parameters"]["sstatedir"]
                setting.sstate_mirror=value_dict["parameters"]["sstatemirror"]
                setting.conf_version=value_dict["parameters"]["conf_version"]
                setting.kernel_image_type=value_dict["parameters"]["kernel_image_type"]
                setting.image_dir=value_dict["parameters"]["image_addr"]
                setting.tmp_dir=value_dict["parameters"]["tmpdir"]
                setting.bb_version=value_dict["parameters"]["bb_version"]
                setting.distro_version=value_dict["parameters"]["distro_version"]
                setting.lconf_version=value_dict["parameters"]["lconf_version"]
                setting.core_base=value_dict["parameters"]["core_base"]
                setting.target_os=value_dict["parameters"]["target_os"]
                setting.image_overhead_factor=value_dict["parameters"]["image_overhead_factor"]
                setting.deployable_image_types=value_dict["parameters"]["deployable_image_types"]
                setting.default_task=value_dict["parameters"]["default_task"]
                setting.tune_pkgarch=value_dict["parameters"]["tune_pkgarch"]
                setting.target_arch=value_dict["parameters"]["target_arch"]
                setting.http_proxy=value_dict["parameters"]["http_proxy"]
                setting.https_proxy=value_dict["parameters"]["https_proxy"]
                setting.ftp_proxy=value_dict["parameters"]["ftp_proxy"]
                if value_dict["parameters"]["image_types"]:
                    setting.image_type_list=value_dict["parameters"]["image_types"]
                pkg_str = ""
                for val in value_dict["formats"]:
                    pkg_str = pkg_str+" "+val
                setting.package_format_list=pkg_str
                toochain_str = ""
                for val in value_dict["machine_sdks"]:
                    toochain_str = toochain_str+" "+val
                setting.build_toolchain_list=toochain_str
                distro_str=""
                for val in value_dict["distros"]:
                    distro_str = distro_str+" "+val
                setting.distro_list=distro_str
                machine_str=""
                for val in value_dict["machines"]:
                    machine_str = machine_str+" "+val
                setting.machine_list=machine_str
                setting.creator=self.userName
                if value_dict.has_key("sanity_check_failed"):
                    setting.note=value_dict["sanity_check_failed"]
                else:
                    setting.note=None
                setting.save()
                if len(Layers.objects.filter(project__name=self.projectName)) == 0:
                    layer_list = value_dict["parameters"]["layer"].strip().split()
                    for val in layer_list:
                        if val.split("/")[-1] == "meta" or val.split("/")[-1] == "meta-hob":
                            types="core"
                        else:
                            types="test"
                        Layers.objects.create(name=val.split("/")[-1], types=types, project=Project.objects.get(name=self.projectName), creator=self.userName, url=str(val))
                else:
                    layer_list = value_dict["parameters"]["layer"].strip().split()
                    for val in layer_list:
                        if not Layers.objects.filter(project__name=self.projectName, name=val.split("/")[-1]):
                            Layers.objects.create(name=val.split("/")[-1], types="test", project=Project.objects.get(name=self.projectName), creator=self.userName, url=str(val))

    def recipe_events(self):
        value_dict = self.xmlRpc.get_events()
        temp_info = {}
        if isinstance(value_dict, dict):
            for key, value in value_dict.iteritems():
                if key == 'pct':
                    temp_info['pct'] = value
                elif key == 'status':
                    pass
                elif key == 'model':
                    RecipeModel.objects.filter(guid=self.guid).delete()
                    RecipeModel.objects.populate(value, self.guid)
                    temp_info['recipe_tree'] = 'recipeTree'
                elif key == 'pkginfolist':
                    temp_info['pkg_tree'] = 'packageTree'
                elif key == 'done':
                    temp_info['commond_complete'] = 'finish'
                    self.recipe_quartz.cancel()
            if temp_info:
                self.queue.append(temp_info)

    def package_events(self):
        value_dict = self.xmlRpc.get_events()
        temp_info = {}
        if isinstance(value_dict, dict):
            for key, value in value_dict.iteritems():
                if key == 'pct':
                    #temp_info['pct'] = value
                    if len(Building.objects.filter(guid=self.guid)) > 0:
                        build_temp = Building.objects.filter(guid=self.guid)[0]
                        if build_temp.build_percent < int(value):
                            build_temp.build_percent = value
                        else:
                            if build_temp.build_percent <= 20:
                                build_temp.build_percent = build_temp.build_percent +1
                        temp_info['pct'] = build_temp.build_percent
                        build_temp.save()
                    #Building.objects.filter(guid=self.guid).update(build_percent=value)
                elif key == 'status':
                    pass
                elif key == 'task' or key == 'taskcompleted' or key == 'buildstarted' \
                or key == 'build_configuration' or key == 'taskfailed' \
                or key == 'queuetaskfailed' or key == 'log_error' \
                or key == 'buildcompleted' or key == 'command_failed' \
                or key == 'no_provider':
                    if isinstance(value, dict):
                        temp_info['state'] = key
                        for k, v in value.iteritems():
                            if 'event' == k:
                                temp_info['task_status'] = v
                            else:
                                temp_info[k] = v
                        self.queue.append(temp_info)
                        temp_info = {}
                elif key == 'done':
                    Building.objects.filter(guid=self.guid).update(build_percent=100, is_finished=True)
                    self.package_quartz.cancel()
                elif key == 'pkginfolist':
                    PackageModel.objects.filter(guid=self.guid).delete()
                    PackageModel.objects.populate(value, self.guid)
                    temp_info['commond_complete'] = 'finish'
                elif key == 'error_msg':
                    temp_info['err_warning'] = value
            if temp_info:
                self.queue.append(temp_info)

    def image_events(self):
        value_dict = self.xmlRpc.get_events()
        temp_info = {}
        if isinstance(value_dict, dict):
            for key, value in value_dict.iteritems():
                if key == 'pct':
                    #temp_info['pct'] = value
                    if len(Building.objects.filter(guid=self.guid)) >0:
                        build_temp = Building.objects.filter(guid=self.guid)[0]
                        if build_temp.build_percent < int(value):
                            build_temp.build_percent = value
                        else:
                            if build_temp.build_percent <= 20:
                                build_temp.build_percent = build_temp.build_percent +1
                        temp_info['pct'] = build_temp.build_percent
                        build_temp.save()
                    #Building.objects.filter(guid=self.guid).update(build_percent=value)
                elif key == 'status':
                    pass
                elif key == 'task' or key == 'taskcompleted' or key == 'buildstarted' \
                or key == 'build_configuration' or key == 'taskfailed' \
                or key == 'queuetaskfailed' or key == 'log_error' \
                or key == 'buildcompleted' or key == 'command_failed' \
                or key == 'no_provider':
                    if isinstance(value, dict):
                        temp_info['state'] = key
                        for k, v in value.iteritems():
                            if 'event' == k:
                                temp_info['task_status'] = v
                            else:
                                temp_info[k] = v
                        self.queue.append(temp_info)
                        temp_info = {}
                elif key == 'done':
                    Building.objects.filter(guid=self.guid).update(build_percent=100, is_finished=True)
                    self.image_quartz.cancel()
                    userSettings = UserSettings.objects.get(settings__project__name=self.projectName, operator__name=self.userName, valid=True)
                    userSettings.valid = False
                    userSettings.save()
                    if value == "Successed_done":
                        #store image
                        user_setting = UserSettings.objects.get(guid=self.guid)
                        builds = Builds.objects.create(guid=self.guid, name=user_setting.baseImage_selected, project=user_setting.settings.project, operator=user_setting.operator)
                        image_queue = self.xmlRpc.get_image_list(user_setting.baseImage_selected, user_setting.machine_selected, user_setting.settings.image_types.strip())

                        image_size = 0.0
                        for item in image_queue:
                            size = (_string_to_size(item["size"]))/(1024*1024)
                            image_size += size
                            images = Images.objects.create(name=item["image_name"], size=size, url=item["ftp_addr"])
                            builds.images.add(images)
                        builds.size = image_size
                        builds.save()
                    else:
                        userSettings.build_error = value
                        userSettings.save()
                    #release bitbake
                    self.xmlRpc.release_one_bitbake()
                elif key == 'pkginfolist':
                    temp_info['commond_complete'] = 'finish'
                elif key == 'error_msg':
                    temp_info['err_warning'] = value
            if temp_info:
                self.queue.append(temp_info)

    def package_image_events(self):
        value_dict = self.xmlRpc.get_events()
        temp_info = {}
        if isinstance(value_dict, dict):
            for key, value in value_dict.iteritems():
                if key == 'pct':
                    #temp_info['pct'] = value
                    if len(Building.objects.filter(guid=self.guid)) > 0:
                        build_temp = Building.objects.filter(guid=self.guid)[0]
                        if build_temp.build_percent < int(value):
                            build_temp.build_percent = value
                        else:
                            if build_temp.build_percent <= 20:
                                build_temp.build_percent = build_temp.build_percent +1
                        temp_info['pct'] = build_temp.build_percent
                        build_temp.save()
                    #Building.objects.filter(guid=self.guid).update(build_percent=value)
                elif key == 'status':
                    pass
                elif key == 'task' or key == 'taskcompleted' or key == 'buildstarted' \
                or key == 'build_configuration' or key == 'taskfailed' \
                or key == 'queuetaskfailed' or key == 'log_error' \
                or key == 'buildcompleted' or key == 'command_failed' \
                or key == 'no_provider':
                    if isinstance(value, dict):
                        temp_info['state'] = key
                        for k, v in value.iteritems():
                            if 'event' == k:
                                temp_info['task_status'] = v
                            else:
                                temp_info[k] = v
                        self.queue.append(temp_info)
                        temp_info = {}
                elif key == 'done':
                    self.package_image_quartz.cancel()
                    Building.objects.filter(guid=self.guid).update(build_percent=100, is_finished=True)
                    temp_info['commond_complete'] = 'finish'
                    userSettings = UserSettings.objects.get(settings__project__name=self.projectName, operator__name=self.userName, valid=True)
                    userSettings.valid = False
                    userSettings.save()
                    if value == "Successed_done":
                        #store image
                        user_setting = UserSettings.objects.get(guid=self.guid)
                        builds = Builds.objects.create(guid=self.guid, name=user_setting.baseImage_selected, project=user_setting.settings.project, operator=user_setting.operator)
                        image_queue = self.xmlRpc.get_image_list(user_setting.baseImage_selected, user_setting.machine_selected, user_setting.settings.image_types.strip())

                        image_size = 0.0
                        for item in image_queue:
                            size = (_string_to_size(item["size"]))/(1024*1024)
                            image_size += size
                            images = Images.objects.create(name=item["image_name"], size=size, url=item["ftp_addr"])
                            builds.images.add(images)
                        builds.size = image_size
                        builds.save()
                    else:
                        userSettings.build_error = value
                        userSettings.save()
                    #release bitbake
                    self.xmlRpc.release_one_bitbake()
                elif key == 'pkginfolist':
                    if Building.objects.filter(guid=self.guid, current_build_task="image", is_finished=True):
                        pass
                    else:
                        PackageModel.objects.filter(guid=self.guid).delete()
                        PackageModel.objects.populate(value, self.guid)
                        temp_info['commond_complete'] = 'finish'
                        Building.objects.filter(guid=self.guid).update(current_build_task="image", build_percent=0, is_finished=False)
                elif key == 'error_msg':
                    temp_info['err_warning'] = value
            if temp_info:
                self.queue.append(temp_info)
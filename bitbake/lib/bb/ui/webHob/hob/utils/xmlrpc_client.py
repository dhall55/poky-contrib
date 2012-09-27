from xmlrpclib import ServerProxy
from settings import *

'''
XmlrpcServer is mainly to used to call management API interface.
'''
class XmlrpcServer():

    def __init__(self, guid, url=MANAGEMENT_SERV_URL):
        self.guid = guid
        self.server = ServerProxy(url, allow_none=True)

    def get_idle_bitbake(self):
        result_str = self.server.reserve_bitbake_server(self.guid)
        if 'allocated server' in result_str:
            return True
        else:
            return False

    def get_initialize_settings_config(self):
        result_str = self.server.initialize_new_build(self.guid)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def update_settings_config(self, config_dict):
        result_str = self.server.parse_configuration(self.guid, config_dict)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def send_request(self, task_command, params=None):
        if 'recipe' in task_command:
            self.parse_recipe(self.guid, params)
        elif 'package' in task_command:
            self.build_package()
        elif 'image' in task_command:
            self.build_image()

    def get_events(self):
        return self.server.get_ret_event(self.guid)

    def parse_recipe(self, buidConfig_dict):
        result_str = self.server.parse_recipe(self.guid, buidConfig_dict)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def build_package(self, buidConfig_dict):
        result_str = self.server.build_package(self.guid, buidConfig_dict)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def build_image(self, buidConfig_dict):
        result_str = self.server.build_image(self.guid, buidConfig_dict)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def build_image_fast(self, buidConfig_dict):
        result_str = self.server.fast_build_image(self.guid, buidConfig_dict)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def stop_build(self, is_force_cancel):
        result_str = self.server.cancel_build(self.guid, is_force_cancel)
        if 'accepted' in result_str:
            return True
        else:
            return False

    def get_image_list(self, baseImage, machine, image_types):
        try:
            return self.server.get_image(self.guid, baseImage, machine, image_types)
        except:
            return []

    def add_bitbake(self, ip, port):
        params_dict = {}
        params_dict["operation"] = "add_one_bitbake"
        params_dict['params'] ={}
        try:
            params_dict['params']['ip'] = ip
            params_dict['params']['port'] = port
            self.server.manage_bitbake_server(params_dict)
            return True
        except:
            return False

    def remove_bitbake(self, ip, port):
        params_dict = {}
        params_dict["operation"] = "delete_one_bitbake"
        params_dict['params'] ={}
        try:
            params_dict['params']['ip'] = ip
            params_dict['params']['port'] = port
            self.server.manage_bitbake_server(params_dict)
            return True
        except:
            return False

    def update_bitbake(self, ip, port, ip_old, port_old):
        params_dict = {}
        params_dict["operation"] = "modify_one_bitbake"
        params_dict['params'] ={}
        try:
            params_dict['params']['ip'] = ip_old
            params_dict['params']['port'] = port_old
            params_dict['params']['new_ip'] = ip
            params_dict['params']['new_port'] = port
            self.server.manage_bitbake_server(params_dict)
            return True
        except:
            return False

    def get_bitbake_all(self, keyword = 'all'):
        params_dict = {}
        params_dict["operation"] = "get_all"
        params_dict['params'] ={}
        params_dict['params']['keyword'] = keyword
        return self.server.manage_bitbake_server(params_dict)

    def reset_bitbake_all(self):
        params_dict = {}
        params_dict["operation"] = "reset_all"
        try:
            self.server.manage_bitbake_server(params_dict)
            return True
        except:
            return False

    def release_one_bitbake(self):
        self.server.release_bitbake_server(self.guid)
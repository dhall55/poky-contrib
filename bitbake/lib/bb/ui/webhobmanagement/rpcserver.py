from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading, thread
import time
import sys
import ftplib
import os

from wsconnection import Connection
from buildtask import BuildTask
from mgtbitbakeserver import MgtBitbakeServers
from setting import FILE_SERV_ADDRESS, TASK_EXECUTING_TIMEOUT_CNT, \
		REQ_CONNECTION_INVAILD_CNT, MAX_REMAIN_REQ_CONNECTION_CNT

class EventQueue:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()

    def pop_queue(self):
        self.lock.acquire()
        item = {'status': '@handling'}
        if self.results:
            item = self.results.pop(0)
        self.lock.release()
        return item

    def push_queue(self, event):
        self.lock.acquire()
        self.results.append(event)
        self.lock.release()

    def reset_queue(self):
        self.lock.acquire()
        while len(self.results):
            self.results.pop(0)
        self.lock.release()

    def insert_queue(self, pos, event):
        self.lock.acquire()
        self.results.insert(pos, event)
        self.lock.release()

class QueueStorage:
    def __init__(self):
        self.queueStorage = {}

    def add_result_queue(self, guid):
        result_queue = EventQueue()
        self.queueStorage[guid] = result_queue
        return result_queue

    def remove_result_queue(self, guid):
        if self.queueStorage.has_key(guid):
            return self.queueStorage[guid].remove(guid)

    def push_user_result_queue(self, guid, event):
        if self.queueStorage.has_key(guid):
            return self.queueStorage[guid].push_queue(event)

    def pop_user_result_queue(self, guid):
        if self.queueStorage.has_key(guid):
            return self.queueStorage[guid].pop_queue()

class RequestApi(object):
    def __init__(self, builders=None):
        self.user_builders = builders

    def get_ret_event(self, guid):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder:
            user_builder.check_req_connect()
        return self.user_builders.assiged_ret_events.pop_user_result_queue(guid)

    def reserve_bitbake_server(self, guid):
        if self.user_builders.mapping_builder_to_user(guid):
            return "allocated server"
        return 'not mapped'

    def release_bitbake_server(self, guid):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.interface: # assert the port and ip is match or not:
            user_builder.release = True
            if user_builder.check_build_logic('cancel_build'):
                self.cancel_build(guid, True)
            else:
                (ip, port) = user_builder.interface
                self.user_builders.bb_serv_mgt.release_bitbake_server(ip, port)
            return "released a server"
        return 'not mapped'

    def manage_bitbake_server(self, operator={}):
        ret_val = ""
        try:
            # r: 'insert 1 rows', f: 'FAILED: ip:127.0.0.1, port:1111 have existed in database'
            if operator['operation'] == 'add_one_bitbake':
                ret_val = self.user_builders.bb_serv_mgt.add_bitbake_server(operator['params']['ip'], operator['params']['port'])
            # r: 'reset successed 2 ret', f:'reset successed 0 ret'
            elif operator['operation'] == 'reset_all':
                ret_val = self.user_builders.bb_serv_mgt.reset_all()
            #[{"status": "free", "ip": "127.0.0.1", "port": 8888, "id": 25, "status_code": 1},
            elif operator['operation'] == 'get_all':
                ret_val = self.user_builders.bb_serv_mgt.get_bitbake_server(operator['params']['keyword'])
            # r:'delete 1 rows', f:'delete 0 rows'
            elif operator['operation'] == 'delete_one_bitbake':
                if (operator['params']).has_key('port'):
                    ret_val = self.user_builders.bb_serv_mgt.delete_bitbake_server(operator['params']['ip'], operator['params']['port'])
                else:
                    ret_val = self.user_builders.bb_serv_mgt.delete_bitbake_server(operator['params']['ip'])
            # r:'update 1 rows', f:'update 0 rows'
            elif operator['operation'] == 'modify_one_bitbake':
                ret_val = self.user_builders.bb_serv_mgt.modify_bitbake_server(operator['params']['ip'], operator['params']['port'], operator['params']['new_ip'], operator['params']['new_port'])

        except Exception, ex:
            import traceback
            ret_val = traceback.format_exc()

        return ret_val

    def initialize_new_build(self, guid):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('initialize_new_build'):
            return user_builder.send_command(['initialize_new_build', user_builder.initialize_new_build, None])
        return 'not start'

    def parse_configuration(self, guid, params):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('parse_configuration'):
            return user_builder.send_command(['parse_configuration', user_builder.generate_configuration, params])
        return 'not start'

    def parse_recipe(self, guid, params):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('parse_recipe'):
            return user_builder.send_command(['parse_recipe', user_builder.generate_recipes, params])
        return 'not start'

    def build_package(self, guid, params):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('build_package'):
            return user_builder.send_command(['build_package', user_builder.generate_packages, params])
        return 'not start'

    def build_image(self, guid, params):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('build_image'):
            return user_builder.send_command(['build_image', user_builder.generate_image, params])
        return 'not start'

    def cancel_build(self, guid, is_force_cancel):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('cancel_build'):
            return user_builder.send_command(['cancel_build', user_builder.cancel_build, is_force_cancel])
        return 'not start'

    def fast_build_image(self, guid, params):
        user_builder = self.user_builders.get_builder(guid)
        if user_builder and user_builder.check_state('fast_build_image'):
            return user_builder.send_command(['fast_build_image', user_builder.fast_build_image, params])
        return 'not start'

    def get_image(self, guid, image_name, curr_mach, image_types):
        user_builder = self.user_builders.get_builder(guid)
        ret_val = []
        if user_builder:
            ret_val = user_builder.get_image_info(image_name, curr_mach, image_types)
            for each_one in ret_val:
                for key, val in each_one.iteritems():
                    if 'ftp_addr' in key:
                        img = val.split("/")[-1]
                        each_one[key] = os.path.join(FILE_SERV_ADDRESS, img)
        else:
            pass
        return ret_val

class BuilderManager(object):

    def __init__(self, bitbake_server_management=None):
        self.builders = []
        self.assiged_ret_events = QueueStorage()
        self.bb_serv_mgt = bitbake_server_management

    def sync_builder_lists(self, builder):
        if builder.release == True:
            self.builders.remove(builder)
            builder.release = False

    def get_builder(self, guid):
        for request_builder in self.builders:
            self.sync_builder_lists(request_builder)
            if request_builder.guid == guid:
                return request_builder
        return None

    def mapping_builder_to_user(self, guid):
        if self.get_builder(guid):
            return True
        free_serv = self.bb_serv_mgt.get_one_free_server()
        if free_serv:
            print free_serv
            try:
                recipe_model = None
                pkgs_model = None
                event_queue = self.assiged_ret_events.add_result_queue(guid)
                buildtask = Builder(guid, (free_serv.ip, free_serv.port), recipe_model, pkgs_model, event_queue)
                self.builders.append(buildtask)
                return True
            except Exception:
                self.assiged_ret_events.remove_result_queue(guid)
                self.bb_serv_mgt.release_bitbake_server(free_serv.ip, free_serv.port)
                return False
        else:
            return False

class Builder(BuildTask):
    (INITIALIZING,
     INITIALIZED,
     CONFIG_SELECTING,
     CONFIG_SELECTED,
     RCPPKGINFO_POPULATING,
     RCPPKGINFO_POPULATED,
     PACKAGE_GENERATING,
     PACKAGE_GENERATED,
     FAST_IMAGE_GENERATING,
     IMAGE_GENERATING,
     IMAGE_GENERATED,
     END_NOOP) = range(12)

    building_sequence_table = {
       'initialize_new_build': INITIALIZING,
       'parse_configuration' : CONFIG_SELECTING,
       'parse_recipe'        : RCPPKGINFO_POPULATING,
       'build_package'       : PACKAGE_GENERATING,
       'build_image'         : IMAGE_GENERATING,
       'fast_build_image'    : FAST_IMAGE_GENERATING,
       'cancel_build'        : END_NOOP
    }

    (bb_unviable_sts, bb_ready_sts, bb_work_sts) = range(3)

    state_2_sch_sts_table = {
       'not_viable'          : bb_unviable_sts,
       'modifying'          : bb_unviable_sts,
       'free'               : bb_ready_sts,
       'allocating'         : bb_ready_sts,
       'allocated'          : bb_ready_sts, #threading monitor (server work monitor) created
       'start'              : bb_work_sts,
       'next_waiting'       : bb_work_sts,
       'busy'               : bb_work_sts,
    }

    def init_builder_context(self, state, renew=True):
        self.info['event_queue'].reset_queue()
        self.process_results_clear()
        if renew:
            self.sch_bb_sts_process_func = [self.do_unviable_pro,
                                            self.do_ready_pro,
                                            self.do_work_pro]
            self.sch_sts = self.state_2_sch_sts_table[state]

        self.thread_exit = False
        self.info['state'] = state

        self.info['response_null_timer_count'] = 0
        self.info['response_null_timeout'] = False
        self.info['task_esmate_timer_count'] = 0
        self.info['task_timeout'] = False

    def is_bb_viable(self):
        if self.info['response_null_timeout']:
            self.info['response_null_timeout'] = False
            print '-----------is inviable-'
            return False
        return True

    """ maybe it should checking the mapping record in db then to change corresponding state
    """
    def is_bb_mapped(self):
        if self.info.has_key('state') and self.info['state'] >= 'allocated':
            return True

        return False

    def is_request_connection_invalid(self):
        if self.info.has_key('request_connection_invaild') and self.info['request_connection_invaild'] == True:
            print '--------request conn invalid'
            return True

        return False

    def is_task_timeout(self):
        if self.info.has_key('task_timeout') and self.info['task_timeout'] == True:
            print '-------executing-timeout'
            return True

        return False

    def release_builder(self):
        global bbservmgt_obj
        bbservmgt_obj.release_bitbake_server(*self.interface)
        self.release = True
        self.set_state('free')

    def report_exc(self, msg=""):
        report = {}
        indicator_words = msg.split(',')[0]
        if 'bitbake exception' in indicator_words:
            number = 8
        elif 'bitbake wrong' in indicator_words:
            number = 4
        elif 'timeout' in indicator_words:
            number = 2
        else:
            number = 1
        report['except_no'] = number
        report['except_request'] = self.info['cmd_request']
        report['except_msg'] = msg
        # insert to current position for ret_queue
        self.info['event_queue'].insert_queue(1, report)

    def scan_bb_server_connection(self):
        if self.info['response_null_timer_count']:
            self.info['response_null_timer_count'] -= 1
            if not self.info['response_null_timer_count']:
                if self.info.has_key('step') and (self.info['step'] not in [self.PACKAGE_GENERATING, self.FAST_IMAGE_GENERATING, self.IMAGE_GENERATING]):
                    self.info['scan_bitbake_timeout'] = True

    def sync_requester_connection(self):
        if self.info['request_connection_timer_count']:
            self.info['request_connection_timer_count'] -= 1
            self.info['request_connection_remain_timeout'] += 1
            if self.info['request_connection_remain_timeout'] > MAX_REMAIN_REQ_CONNECTION_CNT:
                self.info['request_connection_invaild'] = True
        else:
            self.info['request_connection_remain_timeout'] = 0
            self.info['request_connection_invaild'] = True

    def timer(self):
        self.scan_bb_server_connection()
        self.sync_requester_connection()
        if self.info.has_key('task_esmate_timer_count') and self.info['task_esmate_timer_count']:
            if self.info['step'] not in [self.PACKAGE_GENERATING, self.RCPPKGINFO_POPULATING, self.FAST_IMAGE_GENERATING, self.IMAGE_GENERATING]:
                self.info['task_esmate_timer_count'] -= 1
                if not self.info['task_esmate_timer_count']:
                    self.info['task_timeout'] = True

    def set_state(self, tgt_sta):
        if not self.state_2_sch_sts_table.has_key(tgt_sta):
            return False

        curr_sts = self.state_2_sch_sts_table[self.info['state']]
        next_sts = self.state_2_sch_sts_table[tgt_sta]
        if curr_sts < self.bb_work_sts and next_sts >= self.bb_work_sts:
            #self.init_builder_context('start', False)
            pass
        elif curr_sts >= self.bb_work_sts and next_sts < self.bb_work_sts:
            #self.release_builder_context()
            pass
        else:
            pass
        if self.info['state'] != tgt_sta:
            self.info['state'] = tgt_sta
        return True

    def do_ready_pro(self):
        if not self.is_bb_viable():
            self.set_state('not_viable')
        elif self.is_bb_mapped():
            self.set_state('next_waiting')
        else:
            if self.info['state'] == 'allocating':
                self.set_state('allocated')
            elif self.is_request_invalid():
                self.thread_exit = True
                self.release_builder()
            else:
                pass

    def do_work_pro(self):
        if not self.is_bb_viable():
            self.set_state('not_viable')
        elif not self.is_bb_mapped():
            self.set_state('free')
        else:
            resp = ""
            if self.info['state'] == 'next_waiting': #!!or curr_sta == 'allocated'
                self.info['response_null_timeout'] = False
                self.info['response_null_timer_count'] = 0
                # listening request coming in for remain the connection for this user.
                if self.is_request_connection_invalid():
                    self.release = True
                    if self.info['request_connection_timer_count'] > 0:
                        self.report_exc('request connection remain timeout, maybe your net environment \
                                        is bad or some mistaking occur due to client did not received \'done\' ')
                    else:
                        # if self.info['step'] == self.IMAGE_GENERATED: auto released by builder itself
                        # else: no task operation request timeout
                        pass
                else:
                    pass

                # until the release signal be asserted by client initiative or itself.
                if self.release == True:
                    # Note:cases( building completed, initiative released, long no request access to, bitbake no response,
                    # task executing timeout(task timeout, no p_rcp, b_img, b_pkg, f_b_img), client connection invalid(no get_env request))
                    print '----------- auto release'
                    self.thread_exit = True
                    self.release_builder()

            if self.info['state'] == 'start':
                self.info['state'] = 'busy'
                self.info['prev_state'] = 'start'
                self.info['step'] = self.building_sequence_table[self.info['cmd_request']]
                try:
                    if self.info['cmd_params']:
                        resp = (self.info['cmd_func'])(self.info['cmd_params'])
                    else:
                        resp = (self.info['cmd_func'])()

                except Exception as ex:
                    import traceback
                    resp = traceback.format_exc()
                    print 'excep', resp
                    self.info['state'] = 'next_waiting'
                if resp:
                    self.info['event_queue'].push_queue(resp)

                self.info['task_timeout'] = False
                self.info['task_esmate_timer_count'] = TASK_EXECUTING_TIMEOUT_CNT # 1800 30min

            if self.info['state'] == 'busy':
                if self.is_task_timeout():
                    self.info['state'] = 'next_waiting'
                    self.report_exc('the task is braked by bitbake wrong,maybe you should clear the advance settings in db')
                    self.release = True
                else:
                    results = self.polling_event(self.info['cmd_request'])
                    print "----------", results
                    if results:
                        self.info['event_queue'].push_queue(results)
                        if results.get('done', None):
                            self.info['state'] = 'next_waiting'
                            self.info['step'] = (self.IMAGE_GENERATED if self.info['step'] == self.FAST_IMAGE_GENERATING else \
                                                ((self.info['step'] + 1) if self.info['step'] < self.IMAGE_GENERATED else self.info['step']))
                            # the max long time for remain the requester connection is 2hours
                            self.info['request_connection_remain_timeout'] = 0
                            print '---------------------------------------------done-------------', self.info['state']
                        elif (results.get('null', None) == None):
                            self.info['response_null_timer_count'] = 10
                            self.info['response_null_timeout'] = False
                        else:
                            pass
#                    else:
#                        self.info['response_null_timeout'] = 500
            self.info['prev_state'] = self.info['state']

    def do_unviable_pro(self):
        print '-------------------do_unviable_pro'
        if self.is_bb_viable():
            self.set_state('free')
        elif self.is_request_invalid():
            self.thread_exit = True
            self.release_builder()
        else:
            pass

    def schedule(self):
        while (not self.thread_exit):
            self.timer()
            try:
                sch_sts = self.state_2_sch_sts_table[self.info['state']]
                func = self.sch_bb_sts_process_func[sch_sts]
                funky = getattr(self, func.__name__)
                func()
            except Exception as ex:
                import traceback
                print traceback.format_exc()
                funky = None

                self.report_exc('the connection is braked by bitbake exception,you can not start/stop it again and again')
                self.info['state'] = 'not_viable'
                self.thread_exit = True
                self.release_builder()

            time.sleep(1)
        print '------------closed----------------'

    def __init__(self, guid, bb_serv_interface, recipe_model, pkgs_model, event_queue):
        BuildTask.__init__(self, guid, bb_serv_interface, recipe_model, pkgs_model)

        self.info['prev_state'] = self.info['state'] = 'allocated'
        self.info['step'] = self.END_NOOP
        self.info['event_queue'] = event_queue
        self.info['request_connection_timer_count'] = REQ_CONNECTION_INVAILD_CNT # default 50min
        self.info['request_connection_invaild'] = False
        self.info['request_connection_remain_timeout'] = 0

        self.thread = None
        self.release = False
        self.thread_exit = True
        # start builder thread for monitor request connection,
        # if it's timeout,it will auto release bitbake, then guid is invalid.
        self.init_builder_context('allocated', renew=True)
        self.gen_build_process(False, 'allocated')

    def check_state(self, cmd_request=""):
        sch_sts = self.state_2_sch_sts_table[self.info['state']]
        if (sch_sts == self.bb_work_sts or self.info['state'] == 'allocated'):
            if self.info['state'] != 'busy':
                return True
            elif cmd_request == 'cancel_build' and self.info['prev_state'] == 'busy':
                return True

        return False

    def check_build_logic(self, cmd_request=""):
        tgt_step = self.building_sequence_table[cmd_request]
        if tgt_step == self.info['step']:
            return False
        elif cmd_request == 'cancel_build':
            if self.info['step'] == self.RCPPKGINFO_POPULATING \
            or self.info['step'] == self.PACKAGE_GENERATING \
            or self.info['step'] == self.FAST_IMAGE_GENERATING \
            or self.info['step'] == self.IMAGE_GENERATING:
                pass
            else:
                return False
        return True

    def check_req_connect(self, setting_count=REQ_CONNECTION_INVAILD_CNT):# default 50min
        self.info['request_connection_timer_count'] = setting_count
        self.info['request_connection_invaild'] = False

    def gen_build_process(self, daemon=False, trig_sta='start'):
        self.thread = threading.Thread(target=self.schedule)#args = (self,)
        self.thread.setDaemon(daemon)
        self.init_builder_context(trig_sta)
        self.thread.start()

    def send_command(self, command):
        # no queue for requests, because we control the commands coming as serial way
        # for example: next_waiting(for new request),then start(trig task),then busy(processing)
        self.info['cmd_request'], self.info['cmd_func'], self.info['cmd_params'] = command
        self.init_builder_context('start', renew=False)
        return 'accepted'

bbservmgt_obj = MgtBitbakeServers()
manager = BuilderManager(bbservmgt_obj)

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    def __init__( self, interface ):
        SimpleXMLRPCServer.__init__(self,interface, logRequests=False, allow_none=True)

    def serve_forever(self):
        while True:
            self.handle_request()

def main():
    try:
        print "Note: For export to webHob, the webHob corresponding setting need to be changed too !" \

        ip, port = ('localhost', 8001)
        if len(sys.argv) > 1:
            ip = sys.argv[1]
            if len(sys.argv) > 2:
                port = int(sys.argv[2])
        print "Listening: %s, %d" % (ip, port)
        requester = ThreadXMLRPCServer((ip, port))
        requester.register_instance(RequestApi(manager))
        requester.serve_forever()
    except Exception as ex:
        import traceback
        print traceback.format_exc()
        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        print "--- should be like: python rpcserver %s 8001 \n" % local_ip
    sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nquit server'

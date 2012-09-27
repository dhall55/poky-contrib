from runtime import *
from utils import covent_json

class MappingBitbakeServers:
    def __init__(self):
        pass

    def reserver_bitbake_server(self, guid):
        get_row = db.get_row("select id, ip, port, status, status_code from mgt_bitbake_servers where status_code=1")
        if get_row:
             sql = "update mgt_bitbake_servers set status='busy', status_code=2 where id=%s" % get_row.id
             ret = db.update(sql)
        else:
            return "no available bitbake_server to use"

        ret = {'guid':guid,
               'mapping_info':get_row}
#        return covent_json(ret)

    def release_bitbake_server(self, guid):
        #update db to free status
        #kill the thread
        #clean bitbake
        pass

if __name__ == '__main__':
    from pprint import pprint
    m = MappingBitbakeServers()

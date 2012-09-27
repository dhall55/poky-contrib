from runtime import *
from utils import covent_json

class MgtBitbakeServers:
    def __init__(self):
        pass

    def add_bitbake_server(self, ip, port):
        get_row = db.get_row("select * from mgt_bitbake_servers where ip='%s' and port=%s" % (ip, port))
        if get_row is None:
            sql = "insert into mgt_bitbake_servers(ip, port, status, status_code) values('%s', %s, 'free', 1)" % (ip, port)
            ret = db.insert_one(sql)
            return 'insert %s rows' % ret
        else:
            return 'FAILED: ip:%s, port:%s have existed in database' % (ip, port)

    def modify_bitbake_server(self, ip, port, new_ip, new_port):
        sql= "update mgt_bitbake_servers set ip='%s', port=%s where ip='%s' and port='%s'" % (new_ip, new_port, ip, port)
        ret = db.update(sql)
        return 'update %s rows' % ret

    def delete_bitbake_server(self, ip, port=None):
        sql = "delete from mgt_bitbake_servers "
        if port:
            sql+= "where ip='%s' and port=%s" % (ip, port)
        else:
            sql+= "where ip='%s'" % (ip)
        ret = db.delete(sql)
        return 'delete %s rows' % ret

    #keyword = all, free=1, busy=2, down=3
    def get_bitbake_server(self, keyword = 'all'):
        sql = "select id, ip, port, status, status_code from mgt_bitbake_servers "
        if keyword == 'free':
             sql += "where status_code=1"
        elif keyword == 'busy':
            sql += "where status_code=2"
        elif keyword == 'down':
            sql += "where status_code=3"
        ret = db.get_all(sql)
#        return ret
        return covent_json(ret)

    def release_bitbake_server(self, ip, port):
        sql = "update mgt_bitbake_servers set status='free', status_code=1 where ip='%s' and port='%s'" % (ip, port)
        ret = db.update(sql)
        return 'reset successed %ret' % ret

    def reset_all(self):
        sql = "update mgt_bitbake_servers set status='free', status_code=1"
        ret = db.update(sql)
        return 'reset successed %ret' % ret

    def get_one_free_server(self):
        get_row = db.get_row("select id, ip, port, status, status_code from mgt_bitbake_servers where status_code=1")
#        return get_row
        if get_row:
             sql = "update mgt_bitbake_servers set status='busy', status_code=2 where id=%s" % get_row.id
             ret = db.update(sql)
             return get_row
#        else:
#            return 'no available server'

    def get_row_server(self, ip, port):
        get_row = db.get_row("select id, ip, port, status, status_code from mgt_bitbake_servers where ip='%s' and port='%s'" % (ip, port))
        return get_row

    def get_server_status(self, ip, port):
        get_row = db.get_row("select status from mgt_bitbake_servers where ip='%s' and port='%s'" % (ip, port))
        return get_row

class MgtDownloadRecorder:
    def __init__(self):
        pass

    def add_one_recorder(self, guid, url):
        get_row = db.get_row("select * from download where guid=%s" % guid)
        if get_row is None:
            sql = "insert into download(guid, url) values(%s, '%s')" % (guid, url)
            ret = db.insert_one(sql)
            return 'insert %s rows' % ret
        else:
            sql = "update download set url='%s' where guid=%s" % (url, guid)
            ret = db.update(sql)
        return 'updated row from guid=%s' % guid

    def delete_recorder(self, guid=None):
        sql = "delete from download "
        if guid:
            sql+= "where guid=%s" % guid
        ret = db.delete(sql)
        return 'delete %s rows' % ret

    def get_download_url(self, guid):
        get_row = db.get_row("select url from download where guid=%s" % guid)
        return get_row

if __name__ == '__main__':
    from pprint import pprint
#    m = MgtBitbakeServers()
#    print m.add_bitbake_server('127.0.0.1',1111)
#    print m.modify_bitbake_server('127.0.0.3',1111, '127.0.0.2',2223)
#    print m.reset_all()
#    print m.get_bitbake_server()
#    print m.delete_bitbake_server('127.0.0.4',2222)
    n = MgtDownloadRecorder()
    print n.add_one_recorder(111, 'abc')
    print n.add_one_recorder(123, '333')
    print n.add_one_recorder(111, 'bbb')
    print n.get_download_url(111)
    print n.delete_recorder(123)
    print n.get_download_url(123)
    print n.delete_recorder()
    print n.get_download_url(111)


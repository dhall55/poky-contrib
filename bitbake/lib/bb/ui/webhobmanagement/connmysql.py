import sys
import MySQLdb
from  MySQLdb.cursors import DictCursor
from utils import dict_hook

class ConnMysql:
    def __init__(self, host, port, user, passwd, db):
        self.host     = host
        self.port     = port
        self.user     = user
        self.passwd   = passwd
        self.db       = db
        self.conn     = None
        self.cursor   = None
        self.__conn()

    def __conn(self):
        try:
            self.conn = MySQLdb.connect(host=self.host,
                                        port=self.port,
                                        user = self.user,
                                        passwd = self.passwd,
                                        db=self.db)
            self.cursor = self.conn.cursor(DictCursor)
        except MySQLdb.Error,e:
            error_msg = 'Cannot connect to server\nERROR (%s): %s' %(e.args[0],e.args[1])
            sys.exit(error_msg)

    def escape_str(self, str):
#        return self.conn.escape_string(str)
        return MySQLdb.escape_string(str)

    def get_row(self, sql):
        try:
            self.cursor.execute(sql.strip()+' limit 1')
            return dict_hook(self.cursor.fetchone())
        except Exception as e:
            return 'ERROR: get_row: (%s)' % e

    def get_all(self, sql):
        try:
            ret = []
            self.cursor.execute(sql.strip())
            for item in self.cursor.fetchall():
                ret.append(dict_hook(item))
            return ret
        except Exception as e:
            return 'ERROR: get_all: (%s)' % e

    def get_many(self, sql, num):
        try:
            ret = []
            self.cursor.execute(sql.strip())
            for item in self.cursor.fetchmany(num):
                ret.append(dict_hook(item))
            return ret
        except Exception as e:
            return 'ERROR: get_many: (%s)' % e

    def get_id(self,p=0):
        if p == 1:
            return int(self.cursor.lastrowid)
        else:
            return int(self.conn.insert_id())

    def insert_one(self, sql):
        try:
            return self.cursor.execute(sql.strip())
        except Exception as e:
            return 'ERROR: insert_one: (%s)' % e

    def insert_many(self, sql, values):
        try:
            return self.cursor.executemany(sql.strip(), values)
        except Exception as e:
            return 'ERROR: insert_many: (%s)' % e

    def update(self, sql):
        try:
            return self.cursor.execute(sql.strip())
        except Exception as e:
            return 'ERROR: update: (%s)' % e

    def delete(self, sql):
        try:
            return self.cursor.execute(sql.strip())
        except Exception as e:
            return 'ERROR: delete: (%s)' % e

    def __del__(self):
        if self.conn and self.cursor:
            self.conn.close()
            self.cursor.close()

if __name__ == '__main__':
    from pprint import pprint
    db = ConnMysql('localhost', 3306,  'root', '', 'mgt')
    pprint(db.get_many('select * from mgt_bitbake_servers',3))
    print db.get_row("select * from mgt_bitbake_servers where ip='127.0.0.1' and port=8888")
    print db.insert_one("insert into mgt_bitbake_servers(ip, port) values('%s', %s)" % ('127.0.0.1', 8888))
    print db.update("update mgt_bitbake_servers set ip='111111w111' where ip='111111111'")
#    print db.insert_many("insert into bitbake_servers(status, ip, port) values(%s, %s, %s)", [(1,1,1),(1,1,1),(1,1,1)])
#    print db.get_id()
#    print db.delete('delete from bitbake_servers where id =15')

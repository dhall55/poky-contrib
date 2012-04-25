import MySQLdb
def mysql_update(table,col, value):
    try:
        db = MySQLdb.connect(user='root', db='bitbake', passwd='', host='localhost')
        cursor = db.cursor()
        value = db.escape_string(value)
        updatesql = "update %s set %s = '%s' where id =1;" % (table, col, value)
        n = cursor.execute(updatesql)
        db.commit()
        db.close()
        return n
    except MySQLdb.Error,e:
        db.close()
def mysql_select(table):
    try:
        db = MySQLdb.connect(user='root', db='bitbake', passwd='', host='localhost')
        sql = "select * from %s where id =1;" % table
        cursor = db.cursor()
        cursor.execute(sql)
        alldata = cursor.fetchone()
        db.close()
        return alldata
    except MySQLdb.Error,e:
        db.close()
#!/usr/bin/env python
from connmysql import ConnMysql
#from redis_data import RedisData
import setting

db = ConnMysql(setting.HOST,
               setting.PORT,
               setting.USER,
               setting.PASSWD,
               setting.DB)

#redis= RedisData(setting.REDIS_HOST, setting.REDIS_PORT)

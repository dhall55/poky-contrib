#!/usr/bin/env python

#RPC server
RPC_HOST    = 'localhost'
RPC_PORT    = 9999

#REDIS SERVER
REDIS_HOST    = 'localhost'
REDIS_PORT    = 6379

#mysql connection
HOST    = 'localhost'
PORT    = 3306
USER    = 'root'
PASSWD  = 'root'
DB      = 'mgt'

#bitbake servers status
#FREE = 1
#BUSY = 2
#DOWN = 3

# the ftp url format is 'ftp://[user][:password]@ip(or host)[:port]'
# Note: the port is related to the variable 'listen_port=30004' in /etc/vsftpd.conf of FilESERV
FILE_SERV_ADDRESS = "ftp://ftpuser:123456@FSERV321:30004/download/"
# each operation executing timeout except for [parse recipe, building package, building image, fast building]
# if timeout, it means manager can not received the opertion task 'done' from bitbake side
TASK_EXECUTING_TIMEOUT_CNT = 30 * 60 #30min
# if always received the 'null' from the bitbake side, it means bitbake is bad
REQ_CONNECTION_INVAILD_CNT = 10 * 60 #10min
# in some case, the django side can't received the 'done', so it will request the data again and again,
# so add the max long connection timeout for django side. also to no these case[building package, building image]
# Note: there has another case, if user net is too slow, maybe cause this switch in normal processing.
MAX_REMAIN_REQ_CONNECTION_CNT = 2 * 60 * 60 #2hours


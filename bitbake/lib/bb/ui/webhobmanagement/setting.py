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
# Note: !! there has an issue maybe, in some case use the host name to connection ftp server will fault in Ipv6.
FILE_SERV_ADDRESS = "ftp://ftpuser:123456@FSERV321:30004/download/"

# timeout control:
# |-task start(exc_timer:start)------------ ... if not received 'done' then ---(exc_timer:timeout)--auto release
# each operation executing timeout except for [parse recipe, building package, building image, fast building]
# if timeout, it means manager can not received the opertion task 'done' from bitbake side
TASK_EXECUTING_TIMEOUT_CNT = 30 * 60 #30min

# |-task excuting received null(start)-- ... if always received null then ---(timeout)--auto release
# for monitor the bitbake, if always received the 'null' from the bitbake side, it means bitbake is bad
# but in some normal use case the user net is too slow to trig this switch, so closed it.
BITBAKE_RESP_NULL_ALWAYS_CNT = 0

# |-received the get_ret_event request(start)-- ... if long time no request -(timeout)--auto release
# Monitor the request from the webhob side, to charge the guid is ivaild or not
REQ_CONNECTION_INVAILD_CNT = 10 * 60 #default is 10min

# |-received the get_ret_event request(start)-- ... if always get this request no others -(timeout)--auto release
# in some case, the django side can't received the 'done', so it will request the data again and again,
# so add the max long connection timeout for django side. also to no these case[building package, building image]
# Note: there has another case, if user net is too slow, maybe cause this switch in normal processing.
MAX_REMAIN_REQ_CONNECTION_CNT = 3 * 60 * 60 #2hours


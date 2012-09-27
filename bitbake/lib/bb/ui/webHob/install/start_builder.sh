#!/bin/bash

#checking wether 8888 port is not used or not
port=`netstat -tln | grep 8888`
if [ "$port" ];then
    echo "bitbake is running, port 8888 is being used.please kill the process firstly"
    exit 1
fi

cd /home/builder
source poky-contrib/oe-init-build-env build

ip=`/sbin/ifconfig eth0 |grep "inet addr"| cut -f 2 -d ":"|cut -f 1 -d " "`
port=8888

#bitbake -u webhob_webservice $ip:$port &
echo "Waiting...... "
echo "(If you start bitbake with webserice ui for the first time,"
echo "system will compile pseudo firstly, it will take much time."
echo "please waiting......)"

echo "webservice will run@: http://$ip:$port/?wsdl"

cd /home/builder/build
bitbake -u webhob_webservice $ip:$port


#echo "Webservice UI runnning... "
#echo "WSDL is at: http://$ip:$port/?wsdl"

#> /dev/null 2>&1

exit $?

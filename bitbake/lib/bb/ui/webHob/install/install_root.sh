#!/bin/bash

# configurate nfs client
file_serv="10.239.47.176"
file_root="/home/nation/ftp"
file_serv_nfs_root=${file_serv}:${file_root}
# shared folders for nfs_dir to mount
shareimages_dir="/home/builder/build/tmp/deploy/images"
sharelayers_dir="/home/builder/nfsroot"
sstate_dir="/home/builder/build/sstate-cache"
sources_dir="/home/builder/build/downloads"

#install required packages
printf  "\n#[ Installing and checking required packages.... ]\n"
if [ -x "/usr/bin/yum" ];then
    /usr/bin/yum -y groupinstall "development tools"

    /usr/bin/yum -y install python m4 make wget curl ftp tar bzip2 gzip \
    unzip perl texinfo texi2html diffstat openjade \
    docbook-style-dsssl sed docbook-style-xsl docbook-dtds fop xsltproc \
    docbook-utils sed bc eglibc-devel ccache pcre pcre-devel quilt \
    groff linuxdoc-tools patch cmake \
    perl-ExtUtils-MakeMaker tcl-devel gettext chrpath ncurses apr \
    SDL-devel mesa-libGL-devel mesa-libGLU-devel gnome-doc-utils \
    autoconf automake libtool xterm portmap nfs-common

    /usr/bin/yum -y install pytz python-libxml2 python-libxslt1 python-lxml
elif [ -x "/usr/bin/apt-get" ];then
    /usr/bin/apt-get -y install sed wget subversion git-core coreutils \
    unzip texi2html texinfo libsdl1.2-dev docbook-utils fop gawk \
    python-pysqlite2 diffstat make gcc build-essential xsltproc \
    g++ desktop-file-utils chrpath libgl1-mesa-dev libglu1-mesa-dev \
    autoconf automake groff libtool xterm libxml-parser-perl nfs-common portmap

    /usr/bin/apt-get -y install python-tz python-libxml2 python-libxslt1 python-lxml
else
    echo "Currently only supported Ubuntu and Fedora OS"
    exit 0
fi

#install soaplib 1.0
printf  "\n#[ Installing sopalib version 1.0.... ]\n"
tail_wgetrc=`tail -1 /etc/wgetrc`

if [ "$tail_wgetrc" != "http_proxy=http://proxy-shz.intel.com:911/" ];then
    sed -i '$ a\http_proxy=http://proxy-shz.intel.com:911/' /etc/wgetrc
fi

soap=`find /usr/ -name "soaplib" | grep -c "1.0.0"  2>&1`

if [ $soap -eq 0 ];then
    cd /tmp
    wget http://pypi.python.org/packages/source/s/soaplib/soaplib-1.0.0.tar.gz
    /bin/tar zxvf soaplib-1.0.0.tar.gz
    cd soaplib-1.0.0
    python setup.py install
fi

# add builder user
printf  "\n#[ Add user named 'builder' for building images of bitbake.... ]\n"

[ -d "/home/builder" ] || mkdir /home/builder
pass=$(perl -e 'print crypt($ARGV[0], "password")' "builder123")
/usr/sbin/groupadd builder
/usr/sbin/useradd builder -d /home/builder -s /bin/bash -g builder -p $pass
[ ! -d $shareimages_dir ] || umount $shareimages_dir
[ ! -d $sharelayers_dir ] || umount $sharelayers_dir
[ ! -d $sstate_dir ] || umount $sstate_dir
[ ! -d $sources_dir ] || umount $sources_dir
chown -R builder:builder /home/builder

#proxy
if [ ! -f "/home/builder/.bashrc" ];then
    touch /home/builder/.bashrc
    chown -R builder:builder /home/builder/.bashrc
fi

is_proxy=`tail -5 /home/builder/.bashrc |grep -q "proxy" && echo 1 || echo 0`
if [ $is_proxy -eq 0 ];then
    if [ -x "/usr/bin/yum" ];then
        sed -i '$ a\export http_proxy=http://proxy-shz.intel.com:911/' /home/builder/.bashrc
        sed -i '$ a\export ftp_proxy=http://proxy-shz.intel.com:911/' /home/builder/.bashrc
        sed -i '$ a\export https_proxy=http://proxy-shz.intel.com:911/' /home/builder/.bashrc
        sed -i '$ a\export no_proxy=.intel.com' /home/builder/.bashrc
    elif [ -x "/usr/bin/apt-get" ];then
        echo "export http_proxy=http://proxy-shz.intel.com:911/" >> /home/builder/.bashrc
        echo "export ftp_proxy=http://proxy-shz.intel.com:911/" >> /home/builder/.bashrc
        echo "export https_proxy=http://proxy-shz.intel.com:911/" >> /home/builder/.bashrc
        echo "export no_proxy=.intel.com" >> /home/builder/.bashrc
    fi
fi

#proxy config
if [ ! -f "/home/builder/.gitconfig" ];then
    #cp /home/xiaotong/.gitconfig /home/builder/
    #/bin/chown builder:builder /home/builder/.gitconfig
    printf "[core]\n    gitproxy = none for intel.com\n    gitproxy = git-proxy\n    editor = vim\n[merge]\n    tool = vimdiff">/home/builder/.gitconfig
    /bin/chown builder:builder /home/builder/.gitconfig
fi


cd /home/builder
# git poky-contrib
printf  "\n#[ Cloning repo@git://git.yoctoproject.org/poky-contrib.... ]\n"
if [ ! -f "/home/builder/poky-contrib/bitbake/lib/bb/ui/webhob_webservice.py" ];then
    su - builder -c "/usr/bin/git clone git://git.yoctoproject.org/poky-contrib"
    cd /home/builder/poky-contrib
    /usr/bin/git checkout remotes/origin/xtlv/webhob-webservice -b webservice
fi

# create shared folders for bitbake,(nfs client)
if [ ! -d "$sharelayers_dir" ];then
    mkdir -p $sharelayers_dir
    chown -R builder:builder $sharelayers_dir
fi

if [ ! -d ${shareimages_dir} ];then
    mkdir /home/builder/build
    mkdir /home/builder/build/tmp
    mkdir /home/builder/build/tmp/deploy
    mkdir ${shareimages_dir}
    [ -d $sstate_dir ] || mkdir ${sstate_dir}
    [ -d $sources_dir ] || mkdir ${sources_dir}
    chown -R builder:builder /home/builder/build
fi

printf "\ntry to mount ..."
# checking exports of fileserver
nfs_export_root=`showmount -e ${file_serv} | grep ${file_root}`
if [ $? -eq 0 ];then
    echo "checking exports ok: ${file_serv}:$nfs_export_root"
    echo "to mounted .."

    mount -t nfs "${file_serv_nfs_root}/upload" ${sharelayers_dir}
    tail --lines 2 /etc/fstab |  grep "${file_root}/upload"
    if [ $? -ne 0 ];then
        echo "${file_serv_nfs_root}/upload ${sharelayers_dir} nfs user,rw 0 0" >> /etc/fstab
    fi

    mount -t nfs "${file_serv_nfs_root}/download" ${shareimages_dir}
    tail --lines 2 /etc/fstab |  grep "${file_root}/download"
    if [ $? -ne 0 ];then
        echo "${file_serv_nfs_root}/download ${shareimages_dir} nfs user,rw 0 0" >> /etc/fstab
    fi

#    mount -t nfs "${file_serv_nfs_root}/sourcetarball" ${sources_dir}
#    tail --lines 2 /etc/fstab |  grep "${file_root}/sourcetarball"
#    if [ $? -ne 1 ];then
#        echo "${file_serv_nfs_root}/sourcetarball ${sources_dir} nfs user,rw 0 0" >> /etc/fstab
#    fi
#
#    mount -t nfs "${file_serv_nfs_root}/${file_root}/sstate" ${sstate_dir}
#    tail --lines 2 /etc/fstab |  grep "${file_root}/sstate"
#    if [ $? -ne 1 ];then
#        echo "${file_serv_nfs_root}/sstate ${sstate_dir} nfs user,rw 0 0" >> /etc/fstab
#    fi
else
    printf "\nChecking the exported root of nfs serv is failure\n"
fi

#pkill -9 python

printf  "\n#[ Completed installation ]\n"

exit $?

COMPATIBLE_MACHINE = ${MACHINE}

ksrc ?= /home/bruce/poky-kernel/yocto-publish

SRC_URI = "git://${ksrc};fullclone=1;branch=${KBRANCH};name=machine \
           git://${ksrc};noclone=1;branch=wrs_meta;name=meta"        

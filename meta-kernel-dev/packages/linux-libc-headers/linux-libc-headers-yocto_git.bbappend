# If headers specific to the development kernel must be exported
# point ksrc to the same location as the linux-yocto_git recipe.
# KSRC ?= /path/to/kernel/tree

SRC_URI = "git://${KSRC};fullclone=1;branch=${KBRANCH};name=machine \
           git://${KSRC};noclone=1;branch=meta;name=meta"        

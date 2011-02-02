# If headers specific to the development kernel must be exported
# point ksrc to the same location as the linux-yocto_git recipe.
# KSRC ?= /path/to/kernel/tree

SRC_URI = "git://${KSRC};nocheckout=1;branch=${KBRANCH},meta;name=machine,meta"

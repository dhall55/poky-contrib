#
# Copyright (C) 2010 Intel Corporation.
#
require recipes-core/images/poky-image-minimal.bb

SRC_URI = "file://interfaces"

IMAGE_INSTALL += "dropbear mediatomb task-poky-nfs-server"

LICENSE = "MIT"

PR = "r1"

ROOTFS_POSTPROCESS_COMMAND += "setup_target_image ; "

# Manual workaround for lack of auto eth0 (see bug #875)
setup_target_image() {
        install -m 0644 ${WORKDIR}/interfaces ${IMAGE_ROOTFS}/etc/network/interfaces
}


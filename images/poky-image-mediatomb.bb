#
# Copyright (C) 2010 Intel Corporation.
#
require recipes-core/images/poky-image-minimal.bb

SRC_URI = "file://interfaces \
           file://fstab \
	   file://config.xml"

IMAGE_INSTALL += "dropbear mediatomb task-poky-nfs-server"

LICENSE = "MIT"

PR = "r2"

ROOTFS_POSTPROCESS_COMMAND += "setup_target_image ; "

setup_target_image() {
	# Manual workaround for lack of auto eth0 (see bug #875) & static IP for demo
        install -m 0644 ${WORKDIR}/interfaces ${IMAGE_ROOTFS}/etc/network/interfaces

	# Set up mount of /media/storage NFS share
	install -d ${IMAGE_ROOTFS}/media/storage
	install -m 0644 ${WORKDIR}/fstab ${IMAGE_ROOTFS}/etc/fstab

        # Configure mediatomb to autoscan /media/storage
        install -m 0644 ${WORKDIR}/config.xml ${IMAGE_ROOTFS}/etc/mediatomb/config.xml
}


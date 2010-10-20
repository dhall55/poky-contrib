#
# Copyright (C) 2010 Intel Corporation.
# Copyright (C) 2010 Wind River Systems.
#

SRC_URI = "file://fstab \
	file://lighttpd.conf \
	file://exports \
	file://nfsserver \
	file://proftpd.conf \
	file://interfaces \
	file://tftpd-hpa"

PR="r5"

# Extending minimal results in build failure regardless of which
# path I use to poky-image-minimal.bb. Ideally this file would
# contain only the following two lines.
#require "poky-image-minimal.bb"
#IMAGE_INSTALL += "dropbear mediatomb"

# Since the above doesn't work, duplicate minimal and add the
# two packages.
IMAGE_INSTALL = "task-poky-boot task-poky-basic ${ROOTFS_PKGMANAGE} dropbear"

IMAGE_INSTALL += "task-poky-nfs-server"

IMAGE_INSTALL += "mtd-utils"

IMAGE_INSTALL += "e2fsprogs-fsck e2fsprogs-e2fsck e2fsprogs-mke2fs"

IMAGE_INSTALL += "tftp-hpa tftpd-hpa"

IMAGE_INSTALL += "proftpd"

IMAGE_FEATURES += "apps-console-core"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit poky-image

# remove not needed ipkg informations
#ROOTFS_POSTPROCESS_COMMAND += "remove_packaging_data_files ; "

ROOTFS_POSTPROCESS_COMMAND += "setup_target_image ; "

# Manual setup, configuration and workarounds for the NAS image
setup_target_image() {
	mkdir -p ${IMAGE_ROOTFS}/var/adm
	mkdir -p ${IMAGE_ROOTFS}/usr/adm
	mkdir -p ${IMAGE_ROOTFS}/media/storage
	chmod 0777 ${IMAGE_ROOTFS}/media/storage

	install -m 0644 ${WORKDIR}/fstab ${IMAGE_ROOTFS}/etc/fstab
	install -m 0644 ${WORKDIR}/lighttpd.conf ${IMAGE_ROOTFS}/etc/lighttpd.conf
	install -m 0644 ${WORKDIR}/exports ${IMAGE_ROOTFS}/etc/exports
#	install -m 0755 ${WORKDIR}/nfsserver ${IMAGE_ROOTFS}/etc/init.d/nfsserver
	install -m 0644 ${WORKDIR}/proftpd.conf ${IMAGE_ROOTFS}/etc/proftpd.conf
	echo "127.0.0.1       localhost.localdomain           localhost       `cat ${IMAGE_ROOTFS}/etc/hostname`" > ${IMAGE_ROOTFS}/etc/hosts
	install -m 0644 ${WORKDIR}/interfaces ${IMAGE_ROOTFS}/etc/network/interfaces
	install -m 0644 ${WORKDIR}/tftpd-hpa ${IMAGE_ROOTFS}/etc/default/tftpd-hpa

	mkdir -p ${IMAGE_ROOTFS}/media/storage/tftpboot
	for each in 2 3 4 5; do
		ln -s ../init.d/tftp-hpa ${IMAGE_ROOTFS}/etc/rc${each}.d/S20tftp-hpa
		ln -s ../init.d/proftpd ${IMAGE_ROOTFS}/etc/rc${each}.d/S20proftpd
	done
	for each in 1 ; do
		ln -s ../init.d/tftp-hpa ${IMAGE_ROOTFS}/etc/rc${each}.d/K20tftp-hpa
		ln -s ../init.d/proftpd ${IMAGE_ROOTFS}/etc/rc${each}.d/K20proftpd
	done

#	rm -f ${IMAGE_ROOTFS}/etc/init.d/syslog
#	ln -s syslog.sysklogd ${IMAGE_ROOTFS}/etc/init.d/syslog

	# Cron directory is missing...
	mkdir -p ${IMAGE_ROOTFS}/etc/cron.d
}

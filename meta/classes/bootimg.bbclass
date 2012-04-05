# Copyright (C) 2004, Advanced Micro Devices, Inc.  All Rights Reserved
# Released under the MIT license (see packages/COPYING)

# Creates a bootable image using syslinux, your kernel and an optional
# initrd

#
# End result is two things:
#
# 1. A .hddimage file which is an msdos filesystem containing syslinux, a kernel, 
# an initrd and a rootfs image. These can be written to harddisks directly and 
# also booted on USB flash disks (write them there with dd).
#
# 2. A CD .iso image

# Boot process is that the initrd will boot and process which label was selected 
# in syslinux. Actions based on the label are then performed (e.g. installing to 
# an hdd)

# External variables
# ${INITRD} - indicates a filesystem image to use as an initrd (optional)
# ${ROOTFS} - indicates a filesystem image to include as the root filesystem (optional)
# ${AUTO_SYSLINUXCFG} - set this to 1 to enable creating an automatic config
# ${LABELS} - a list of targets for the automatic config
# ${APPEND} - an override list of append strings for each label
# ${SYSLINUX_OPTS} - additional options to add to the syslinux file ';' delimited 

do_bootimg[depends] += "dosfstools-native:do_populate_sysroot \
                       syslinux:do_populate_sysroot \
                       syslinux-native:do_populate_sysroot \
		       mtools-native:do_populate_sysroot \
		       cdrtools-native:do_populate_sysroot"

PACKAGES = " "
EXCLUDE_FROM_WORLD = "1"

HDDDIR = "${S}/hdd/boot"
ISODIR = "${S}/cd/isolinux"

BOOTIMG_VOLUME_ID   ?= "boot"
BOOTIMG_EXTRA_SPACE ?= "512"

# Get the build_syslinux_cfg() function from the syslinux class

SYSLINUXCFG  = "${HDDDIR}/syslinux.cfg"
SYSLINUXMENU = "${HDDDIR}/menu"

inherit syslinux
		
build_boot_bin() {
	install -d ${HDDDIR}
	install -m 0644 ${STAGING_DIR_HOST}/kernel/bzImage \
	${HDDDIR}/vmlinuz

	if [ -n "${INITRD}" ] && [ -s "${INITRD}" ]; then 
    		install -m 0644 ${INITRD} ${HDDDIR}/initrd
	fi

	if [ -n "${ROOTFS}" ] && [ -s "${ROOTFS}" ]; then 
    		install -m 0644 ${ROOTFS} ${HDDDIR}/rootfs.img
	fi

	install -m 444 ${STAGING_LIBDIR}/syslinux/ldlinux.sys ${HDDDIR}/ldlinux.sys

	# Determine the 1024 byte block count for the final image.
	BLOCKS=`du --apparent-size -ks ${HDDDIR} | cut -f 1`
	SIZE=`expr $BLOCKS + ${BOOTIMG_EXTRA_SPACE}`

	# Ensure total sectors is an integral number of sectors per
	# track or mcopy will complain. Sectors are 512 bytes, and and
	# we generate images with 32 sectors per track. This calculation
	# is done in blocks, which are twice the size of sectors, thus
	# the 16 instead of 32.
	SIZE=$(expr $SIZE + $(expr 16 - $(expr $SIZE % 16)))

	IMG=${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.hddimg
	mkdosfs -n ${BOOTIMG_VOLUME_ID} -S 512 -C ${IMG} ${SIZE}
	# Copy HDDDIR recursively into the image file directly
	mcopy -i ${IMG} -s ${HDDDIR}/* ::/

	syslinux ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.hddimg
	chmod 644 ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.hddimg

	cd ${DEPLOY_DIR_IMAGE}
	rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.hddimg
	ln -s ${IMAGE_NAME}.hddimg ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.hddimg
	
	#Create an ISO if we have an INITRD
	if [ -n "${INITRD}" ] && [ -s "${INITRD}" ] && [ "${NOISO}" != "1" ] ; then
		install -d ${ISODIR}

		# Install the kernel

		install -m 0644 ${STAGING_DIR_HOST}/kernel/bzImage \
		        ${ISODIR}/vmlinuz

		# Install the configuration files

		cp ${HDDDIR}/syslinux.cfg ${ISODIR}/isolinux.cfg

		if [ -f ${SYSLINUXMENU} ]; then
			cp ${SYSLINUXMENU} ${ISODIR}
		fi

		install -m 0644 ${INITRD} ${ISODIR}/initrd

		if [ -n "${ROOTFS}" ] && [ -s "${ROOTFS}" ]; then 
			install -m 0644 ${ROOTFS} ${ISODIR}/rootfs.img
		fi

		# And install the syslinux stuff 
		cp ${STAGING_LIBDIR}/syslinux/isolinux.bin ${ISODIR}

		mkisofs -V ${BOOTIMG_VOLUME_ID} \
		-o ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.iso \
		-b isolinux/isolinux.bin -c isolinux/boot.cat -r \
		-no-emul-boot -boot-load-size 4 -boot-info-table \
		${S}/cd/

		cd ${DEPLOY_DIR_IMAGE}
		rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.iso
		ln -s ${IMAGE_NAME}.iso ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.iso

	fi
} 

python do_bootimg() {
	bb.build.exec_func('build_syslinux_cfg', d)
	bb.build.exec_func('build_boot_bin', d)
}

addtask bootimg before do_build
do_bootimg[nostamp] = "1"

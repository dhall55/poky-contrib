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

# External variables (also used by syslinux.bbclass)
# ${INITRD} - indicates a filesystem image to use as an initrd (optional)
# ${NOISO}  - skip building the ISO image if set to 1
# ${ROOTFS} - indicates a filesystem image to include as the root filesystem (optional)

do_bootimg[depends] += "dosfstools-native:do_populate_sysroot \
                        mtools-native:do_populate_sysroot \
                        cdrtools-native:do_populate_sysroot"

PACKAGES = " "
EXCLUDE_FROM_WORLD = "1"

HDDDIR = "${S}/hdd/boot"
ISODIR = "${S}/cd"

BOOTIMG_VOLUME_ID   ?= "boot"
BOOTIMG_EXTRA_SPACE ?= "512"

EFI = ${@base_contains("MACHINE_FEATURES", "efi", "1", "0", d)}
EFI_CLASS = ${@base_contains("MACHINE_FEATURES", "efi", "grub-efi", "dummy", d)}

inherit syslinux
inherit ${EFI_CLASS}


build_iso() {
	# Only create an ISO if we have an INITRD and NOISO was not set
	if [ -z "${INITRD}" ] || [ ! -s "${INITRD}" ] || [ "${NOISO}" = "1" ]; then
		bbnote "ISO image will not be created."
		return
	fi

	install -d ${ISODIR}

	syslinux_iso_populate
	if [ "${EFI}" = "1" ]; then
		grubefi_iso_populate
	fi

	mkisofs -V ${BOOTIMG_VOLUME_ID} \
	        -o ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.iso \
		-b ${ISO_BOOTIMG} -c ${ISO_BOOTCAT} -r \
		${MKISOFS_OPTIONS} ${ISODIR}

	cd ${DEPLOY_DIR_IMAGE}
	rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.iso
	ln -s ${IMAGE_NAME}.iso ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.iso
}

build_hddimg() {
	install -d ${HDDDIR}

	syslinux_hddimg_populate
	if [ "${EFI}" = "1" ]; then
		grubefi_hddimg_populate
	fi

	# Determine the block count for the final image
	BLOCKS=`du -bks ${HDDDIR} | cut -f 1`
	SIZE=`expr $BLOCKS + ${BOOTIMG_EXTRA_SPACE}`

	mkdosfs -n ${BOOTIMG_VOLUME_ID} -d ${HDDDIR} \
	        -C ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.hddimg $SIZE 

	syslinux_hddimg_install

	chmod 644 ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.hddimg

	cd ${DEPLOY_DIR_IMAGE}
	rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.hddimg
	ln -s ${IMAGE_NAME}.hddimg ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.hddimg
}

python do_bootimg() {
	bb.build.exec_func('build_syslinux_cfg', d)
	if d.getVar("EFI", True) == "1":
		bb.build.exec_func('build_grub_cfg', d)
	bb.build.exec_func('build_hddimg', d)
	bb.build.exec_func('build_iso', d)
}

addtask bootimg before do_build
do_bootimg[nostamp] = "1"

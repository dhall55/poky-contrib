
AUTO_SYSLINUXCFG = "1"
INITRD = "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.ext3.lzma"
SYSLINUX_ROOT = "root=/dev/ram0 "
#SYSLINUX_TIMEOUT ?= "10"
#SYSLINUX_LABELS ?= "boot install"
LABELS_append = " ${SYSLINUX_LABELS} "
ROOTFS = ""

#do_bootimg[depends] += "${INITRD_IMAGE}:do_rootfs"
do_bootimg[depends] += "${IMAGE_BASENAME}:do_rootfs"

inherit bootimg

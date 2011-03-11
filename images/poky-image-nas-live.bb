DESCRIPTION = "Bootable NAS Image"

require recipes-core/images/poky-image-live.inc

LABELS += "boot install"

ROOTFS = "${DEPLOY_DIR_IMAGE}/poky-image-nas-${MACHINE}.ext3"

LICENSE = "MIT"

do_bootimg[depends] += "poky-image-nas:do_rootfs"

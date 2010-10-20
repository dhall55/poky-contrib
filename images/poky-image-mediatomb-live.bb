DESCRIPTION = "Bootable Live Media Renderer Image"

require recipes-core/images/poky-image-live.inc

LABELS += "boot install"

ROOTFS = "${DEPLOY_DIR_IMAGE}/poky-image-mediatomb-${MACHINE}.ext3"

LICENSE = "MIT"

do_bootimg[depends] += "poky-image-mediatomb:do_rootfs"

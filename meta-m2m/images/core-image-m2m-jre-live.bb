DESCRIPTION = "Bootable Live M2M JRE Image"

require recipes-core/images/core-image-live.inc

LABELS += "boot install"

ROOTFS = "${DEPLOY_DIR_IMAGE}/core-image-m2m-jre-${MACHINE}.ext3"

LICENSE = "MIT"

do_bootimg[depends] += "core-image-m2m-jre:do_rootfs"
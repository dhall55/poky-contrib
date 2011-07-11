DESCRIPTION = "Bootable Live M2M JDK Image"

require recipes-core/images/core-image-live.inc

LABELS += "boot install"

ROOTFS = "${DEPLOY_DIR_IMAGE}/core-image-m2m-jdk-${MACHINE}.ext3"

LICENSE = "MIT"

do_bootimg[depends] += "core-image-m2m-jdk:do_rootfs"
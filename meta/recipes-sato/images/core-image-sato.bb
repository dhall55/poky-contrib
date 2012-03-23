#
# Copyright (C) 2007 OpenedHand Ltd.
#
DESCRIPTION = "An image with Sato support, a mobile environment and visual \
style that works well with mobile devices."

IMAGE_FEATURES += "apps-console-core ${SATO_IMAGE_FEATURES}"

LICENSE = "MIT"

inherit core-image

LIVE = "${@base_contains('IMAGE_FSTYPES', 'live', 'yes', 'no', d)}"

do_check_unionfs() {
        if [ "${NOISO}" = "1" ]; then
                return
        fi

        if [ "${LIVE}" = "yes" ] && ! grep -q "CONFIG_UNION_FS=y" ${STAGING_KERNEL_DIR}/.config; then
                rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}.iso
                rm -f ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.iso
                bbfatal "Building LIVE CD without UNION FS enabled in kernel"
        fi
}

addtask check_unionfs before do_build after do_bootimg

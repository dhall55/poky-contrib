LICENSE = "MIT"
PR="r0"

LIC_FILES_CHKSUM = "file://${COREBASE}/LICENSE;md5=3f40d7994397109285ec7b81fdeb3b58 \
                    file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"


DEPENDS += "task-core-gtk-directfb"

RDEPENDS_${PN} += " \
	task-core-gtk-directfb-base \
	"

inherit core-image

IMAGE_INSTALL += "\
	${POKY_BASE_INSTALL} \
	task-core-basic \
	module-init-tools \
	task-core-gtk-directfb-base \
"

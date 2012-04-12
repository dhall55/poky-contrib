# Support for device tree generation
FILES_kernel-devicetree = "/boot/devicetree*"
KERNEL_DEVICETREE_FLAGS = "-R 8 -p 0x3000"

python __anonymous () {
    import bb

    devicetree = bb.data.getVar("KERNEL_DEVICETREE", d, 1) or ''
    if devicetree:
	depends = bb.data.getVar("DEPENDS", d, 1)
	bb.data.setVar("DEPENDS", "%s dtc-native" % depends, d)
	packages = bb.data.getVar("PACKAGES", d, 1)
	bb.data.setVar("PACKAGES", "%s kernel-devicetree" % packages, d)
}

do_install_append() {
    if test -n "${KERNEL_DEVICETREE}"; then
	dtc -I dts -O dtb ${KERNEL_DEVICETREE_FLAGS} -o devicetree ${KERNEL_DEVICETREE}
	install -m 0644 devicetree ${D}/boot/devicetree-${KERNEL_VERSION}
	install -d ${DEPLOYDIR}
	install -m 0644 devicetree ${DEPLOYDIR}/${KERNEL_IMAGE_BASE_NAME}.dtb
	cd ${DEPLOYDIR}
	rm -f ${KERNEL_IMAGE_SYMLINK_NAME}.dtb
	ln -sf ${KERNEL_IMAGE_BASE_NAME}.dtb ${KERNEL_IMAGE_SYMLINK_NAME}.dtb
    fi
}


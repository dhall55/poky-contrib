inherit module_strip

inherit kernel-arch

export OS = "${TARGET_OS}"
export CROSS_COMPILE = "${TARGET_PREFIX}"

export KERNEL_VERSION = "${@base_read_file('${STAGING_KERNEL_DIR}/kernel-abiversion')}"
KERNEL_OBJECT_SUFFIX = ".ko"

# kernel modules are generally machine specific
PACKAGE_ARCH = "${MACHINE_ARCH}"

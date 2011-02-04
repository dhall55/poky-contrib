require recipes-kernel/linux-libc-headers/linux-libc-headers.inc

# FIXME: these three probably belong in linux-libc-headers.inc
INHIBIT_DEFAULT_DEPS = "1"
DEPENDS += "unifdef-native"
PROVIDES = "linux-libc-headers"

PR = "r0"

# FIXME: probably need an include to share with the kernel recipe
SRC_URI = "git://git.linaro.org/kernel/linux-linaro-2.6.35.git;protocol=git"
SRCREV = "2207e446f6559ee5c51332c0f64a8a06f48f4d5f"

# The following functions could probably all go in the include as well
set_arch() {
	case ${TARGET_ARCH} in
		arm*)     ARCH=arm ;;
	esac
}

do_configure() {
	set_arch
	oe_runmake allnoconfig ARCH=$ARCH
}

do_compile () {
}

do_install() {
	set_arch
	oe_runmake headers_install INSTALL_HDR_PATH=${D}${exec_prefix} ARCH=$ARCH
	# FIXME: should we keep this?
	# Kernel should not be exporting this header
	#rm -f ${D}${exec_prefix}/include/scsi/scsi.h
}

BBCLASSEXTEND = "nativesdk"

S = "${WORKDIR}/git"

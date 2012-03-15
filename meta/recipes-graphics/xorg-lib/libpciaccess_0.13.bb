SUMMARY = "Generic PCI access library for X"

DESCRIPTION = "libpciaccess provides functionality for X to access the \
PCI bus and devices in a platform-independant way."

require xorg-lib-common.inc

LICENSE = "MIT & MIT-style"
LIC_FILES_CHKSUM = "file://COPYING;md5=de01cb89a769dc657d4c321c209ce4fc"

PR = "r0"

DEPENDS += "xproto virtual/libx11"

SRC_URI[md5sum] = "2604307ba43c76ee8aec11ea137ae1e8"
SRC_URI[sha256sum] = "24368520b0947487ec73729e3c97c95f3d9bf83704a910bb0abe1d5a63df32fd"

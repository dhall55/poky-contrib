SUMMARY = "LibYAML is a YAML 1.1 parser and emitter written in C."
DESCRIPTION = "LibYAML is a C library for parsing and emitting data in YAML 1.1, \
a human-readable data serialization format. "
HOMEPAGE = "http://pyyaml.org/wiki/LibYAML"
SECTION = "libs/devel"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=6015f088759b10e0bc2bf64898d4ae17"

SRC_URI = "http://pyyaml.org/download/libyaml/yaml-${PV}.tar.gz"

SRC_URI[md5sum] = "36c852831d02cf90508c29852361d01b"
SRC_URI[sha256sum] = "7bf81554ae5ab2d9b6977da398ea789722e0db75b86bffdaeb4e66d961de6a37"

S = "${WORKDIR}/yaml-${PV}"

inherit autotools

FILESEXTRAPATHS_append := "${THISDIR}/dbus-${PV}"
include recipes-core/dbus/dbus.inc

PR = "${INC_PR}.0"

SRC_URI[md5sum] = "79eca2f2c1894ac347acce128314428b"
SRC_URI[sha256sum] = "103bdcd261a13140730b5fa69f56a98ab5c89ba3f0116ea62fcfd639520d5aaf"

DEPENDS += "python-pygobject-native python-dbus-native dbus-glib dbus"
RDEPENDS_${PN} = "dbus-x11"
RPROVIDES_${PN} = ""

TEST_PATH = "${libdir}/${BPN}"

EXTRA_OECONF += "--enable-tests --enable-embedded-tests --enable-verbose-mode --with-dbus-test-dir=${TEST_PATH}"

export DBUS_GLIB_CFLAGS="-I${STAGING_DIR_HOST}${includedir}/dbus-1.0"
export DBUS_GLIB_LIBS="-ldbus-glib-1"

S = "${WORKDIR}/dbus-${PV}"

# Add test wrapper
SRC_URI += "file://run_test.sh"

# We don't want to overwrite dbus in sysroot. Just want to package the tests
do_populate_sysroot[noexec] = "1"

PACKAGES = "${PN}-dbg ${PN}"

FILES_${PN} = "${TEST_PATH}"
FILES_${PN}-dbg = "${TEST_PATH}/bus/.debug \
		   ${TEST_PATH}/dbus/.debug \
		   ${TEST_PATH}/test/.debug \
		   /usr/src/debug"

BUS_TESTS = "bus-test bus-test-system bus-test-launch-helper dbus-daemon-launch-helper-test"
DBUS_TESTS = "dbus-test"
TEST = "dbus-test-runner spawn-test .libs/test-dbus-daemon .libs/test-loopback test-sleep-forever \
	test-segfault shell-test test-exit .libs/test-marshal test-refs test-shell-service \
	.libs/test-corrupt test-syslog test-names .libs/test-relay test-service"

do_install () {
	install -d ${D}/${TEST_PATH}/test/data
	install -d ${D}/${TEST_PATH}/dbus
	install -d ${D}/${TEST_PATH}/bus

	cp -r ${S}/test/data/* ${D}/${TEST_PATH}/test/data

	for file in ${BUS_TESTS}; do
		install -m 766 ${S}/bus/${file} ${D}/${TEST_PATH}/bus
	done

	for file in ${DBUS_TESTS}; do
		install -m 766 ${S}/dbus/${file} ${D}/${TEST_PATH}/dbus
	done

	for file in ${TEST}; do
		install -m 766 ${S}/test/${file} ${D}/${TEST_PATH}/test
	done

	install -m 766 ${WORKDIR}/run_test.sh ${D}/${TEST_PATH}
}

BBCLASSEXTEND = ""

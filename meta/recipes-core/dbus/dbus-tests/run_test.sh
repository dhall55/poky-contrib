#!/bin/sh

# Tests location
export DBUS_TEST_HOMEDIR=/usr/lib/dbus-tests
# Tests data location
export DBUS_TEST_DATA=${DBUS_TEST_HOMEDIR}/test/data

TESTS=" \
	bus/bus-test \
	bus/bus-test-system \
	dbus/dbus-test \
	bus/bus-test-launch-helper \
	test/shell-test \
	test/test-corrupt \
	test/test-dbus-daemon \
	test/test-loopback \
	test/test-marshal \
	test/test-relay \
	test/test-syslog \
	test/test-refs"

${DBUS_TEST_HOMEDIR}/test/dbus-test-runner ${DBUS_TEST_HOMEDIR} ${TESTS}

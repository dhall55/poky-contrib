require gcc-configure-common.inc
require gcc-multilib-config.inc

EXTRA_OECONF_PATHS = " \
    --with-local-prefix=${STAGING_DIR_TARGET}${prefix} \
    --with-gxx-include-dir=${includedir}/c++/"

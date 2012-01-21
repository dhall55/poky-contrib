require gcc-configure-common.inc
require gcc-multilib-config.inc

EXTRA_OECONF_PATHS = " \
    --with-gxx-include-dir=${includedir}/c++/"

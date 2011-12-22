inherit cross-canadian

DESCRIPTION = "cross-canadian gdb for ${TARGET_ARCH} target - GNU debugger"
PN = "gdb-cross-canadian-${TRANSLATED_TARGET_ARCH}"
BPN = "gdb"

DEPENDS = "nativesdk-ncurses nativesdk-expat nativesdk-gettext nativesdk-readline nativesdk-python"
RDEPENDS += "nativesdk-python-core nativesdk-python-lang nativesdk-python-re \
             nativesdk-python-codecs nativesdk-python-netclient"

EXTRA_OECONF_append = "--with-python=${WORKDIR}/python"

do_configure_prepend() {
cat > ${WORKDIR}/python << EOF
#! /bin/sh
case "\$2" in
        --includes) echo "-I${STAGING_INCDIR}/python${PYTHON_BASEVERSION}/" ;;
        --ldflags) echo "-L${STAGING_LIBDIR}/../python${PYTHON_BASEVERSION}/config -lpthread -ldl -lutil -lm -lpython${PYTHON_BASEVERSION}" ;;
        --exec-prefix) echo "/usr" ;;
        *) exit 1 ;;
esac
exit 0
EOF
        chmod +x ${WORKDIR}/python
}


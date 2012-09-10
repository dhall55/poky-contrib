require opkg.inc

SRC_URI = "svn://opkg.googlecode.com/svn;module=trunk;protocol=http \
           file://add_vercmp.patch \
           file://add_uname_support.patch \
           file://fix_installorder.patch \
           file://offline_postinstall.patch\
           file://track_parents.patch \
           file://conf_override.patch \
           file://update_icon_cache_trigger_script.patch \
"

S = "${WORKDIR}/trunk"

SRCREV = "633"
PV = "0.1.8+svnr${SRCPV}"

PR = "${INC_PR}.2"

do_configure_prepend() {
	if [ -f ${S}/intercept/update_icon_cache ]; then
		chmod +x ${S}/intercept/update_icon_cache
	fi
}

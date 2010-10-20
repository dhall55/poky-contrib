FILESEXTRAPATHS := "${THISDIR}/${PN}"
SRC_URI_append_routerstationpro = " file://linux-routerstationpro.cfg \
	file://linux-routerstationpro-${RSP_ROOT}.cfg"

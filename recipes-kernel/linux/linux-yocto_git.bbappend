FILESEXTRAPATHS := "${THISDIR}/${PN}"
# Disable OMAP4 which breaks audio for the BeagleBoard xM 3740 CPU
# Disable MUSB which causes compiler failures with <plat/control.h>
SRC_URI_append_beagleboard = " file://beagleboard-omap4-musb.cfg"
SRC_URI_append_routerstationpro = " file://routerstationpro-nfsd.cfg"


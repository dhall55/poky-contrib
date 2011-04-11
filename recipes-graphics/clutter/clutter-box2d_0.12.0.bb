require clutter-box2d.inc

PR = "r0"

SRC_URI = "git://git.gnome.org/clutter-box2d;protocol=git;tag=CLUTTER_BOX2D_0_12_0"

S = "${WORKDIR}/git"

LIC_FILES_CHKSUM = "file://COPYING;md5=7fbc338309ac38fefcd64b04bb903e34"

BASE_CONF += "--disable-introspection"

do_configure_prepend () {
	# Disable DOLT
	sed -i -e 's/^DOLT//' ${S}/configure.ac
}

SRC_URI[md5sum] = "51618976ca6a5d536c4eac5f0e120d9d"
SRC_URI[sha256sum] = "1e42d0cea429e4dc953a1f652672dbd322b3938846e99bab35f463de6fd8ae7f"

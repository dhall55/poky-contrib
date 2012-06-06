SUMMARY = "The basic file, shell and text manipulation utilities."
DESCRIPTION = "The GNU Core Utilities provide the basic file, shell and text \
manipulation utilities. These are the core utilities which are expected to exist on \
every system."

HOMEPAGE = "http://www.gnu.org/software/coreutils/"
BUGTRACKER = "http://debbugs.gnu.org/coreutils"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe \
                    file://src/ls.c;startline=4;endline=16;md5=482a96d4f25010a4e13f8743e0c3685e"
PR = "r3"
DEPENDS = "coreutils-native-${PV}"
DEPENDS_virtclass-native = "gettext-native"

inherit autotools gettext

SRC_URI_BASE = "${GNU_MIRROR}/coreutils/${BP}.tar.bz2 \
           file://gnulib_m4.patch \
           file://futimens.patch \
           file://coreutils-ls-x.patch \
           file://coreutils-6.9-cp-i-u.patch \
           file://coreutils-i18n.patch \
           file://coreutils-overflow.patch \
           file://coreutils-fix-install.patch \
           file://man-touch.patch \
           file://coreutils_fix_for_automake-1.12.patch \
           "

SRC_URI = "${SRC_URI_BASE} file://fix_for_manpage_building.patch"
SRC_URI_virtclass-native = "${SRC_URI_BASE}"

SRC_URI[md5sum] = "c9607d8495f16e98906e7ed2d9751a06"
SRC_URI[sha256sum] = "89c2895ad157de50e53298b22d91db116ee4e1dd3fdf4019260254e2e31497b0"

# [ gets a special treatment and is not included in this
bindir_progs = "base64 basename cksum comm csplit cut dir dircolors dirname du \
                env expand expr factor fmt fold groups head hostid id install \
                join link logname md5sum mkfifo nice nl nohup od paste pathchk \
                pinky pr printenv printf ptx readlink seq sha1sum sha224sum sha256sum \
                sha384sum sha512sum shred shuf sort split stat sum tac tail tee test \
                tr tsort tty unexpand uniq unlink users vdir wc who whoami yes uptime"

# hostname gets a special treatment and is not included in this
base_bindir_progs = "cat chgrp chmod chown cp date dd echo false kill ln ls mkdir \
                     mknod mv pwd rm rmdir sleep stty sync touch true uname hostname"

sbindir_progs= "chroot"

do_install() {
	autotools_do_install

	install -d ${D}${base_bindir}
	[ "${bindir}" != "${base_bindir}" ] && for i in ${base_bindir_progs}; do mv ${D}${bindir}/$i ${D}${base_bindir}/$i; done

	install -d ${D}${sbindir}
	[ "${bindir}" != "${sbindir}" ] && for i in ${sbindir_progs}; do mv ${D}${bindir}/$i ${D}${sbindir}/$i; done

	# [ requires special handling because [.coreutils will cause the sed stuff
	# in update-alternatives to fail, therefore use lbracket - the name used
	# for the actual source file.
	mv ${D}${bindir}/[ ${D}${bindir}/lbracket.${BPN}
}

inherit update-alternatives

ALTERNATIVE_PRIORITY = "100"

ALTERNATIVE_${PN} = "lbraket ${bindir_progs} ${base_bindir_progs} ${sbindir_progs}"

ALTERNATIVE_PRIORITY[uptime] = "10"
ALTERNATIVE_PRIORITY[hostname] = "10"

ALTERNATIVE_LINK_NAME[lbracket] = "${bindir}/["
ALTERNATIVE_TARGET[lbracket] = "${bindir}/lbracket.${BPN}"

python __anonymous() {
	for prog in d.getVar('base_bindir_progs', True).split():
		d.setVarFlag('ALTERNATIVE_LINK_NAME', prog, '%s/%s' % (d.getVar('base_bindir', True), prog))

	for prog in d.getVar('sbindir_progs', True).split():
		d.setVarFlag('ALTERNATIVE_LINK_NAME', prog, '%s/%s' % (d.getVar('sbindir', True), prog))
}

BBCLASSEXTEND = "native"
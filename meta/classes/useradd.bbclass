# base-passwd-cross provides the default passwd and group files in the
# target sysroot, and shadow -native and -sysroot provide the utilities
# and support files needed to add and modify user and group accounts
DEPENDS_append = "${USERADDDEPENDS}"
USERADDDEPENDS = " base-passwd shadow-native shadow-sysroot shadow"
USERADDDEPENDS_virtclass-cross = ""
USERADDDEPENDS_virtclass-native = ""
USERADDDEPENDS_virtclass-nativesdk = ""

# This preinstall function can be run in four different contexts:
#
# a) Before do_install
# b) At do_populate_sysroot_setscene when installing from sstate packages
# c) As the preinst script in the target package at do_rootfs time
# d) As the preinst script in the target package on device as a package upgrade
#
def useradd_preinst(d):
	import re

	sysroot = ""
	opt = ""

	dir = d.getVar('STAGING_DIR_TARGET', True)
	if dir:
		# Installing into a sysroot
		sysroot = dir
		opt = "--root %s" % dir

		# Add groups and users defined for all recipe packages
		groupadd_param = get_all_cmd_params(d, 'group')
		useradd_param = get_all_cmd_params(d, 'user')
	else:
		# Installing onto a target
		# Add groups and users defined only for this package
		groupadd_param = d.getVar('GROUPADD_PARAM', True)
		useradd_param = d.getVar('GROUPADD_PARAM', True)

	group_file = '%s/etc/group' % sysroot
	user_file = '%s/etc/passwd' % sysroot

	# Use the locking of bb to the group/passwd file to avoid the
	# locking issue of groupadd/useradd
	group_lock = '%s.locked' % group_file
	user_lock = '%s.locked' % user_file
	lockfiles = [group_lock, user_lock]

	with bb.utils.fileslocked(lockfiles):
		# Perform group additions first, since user additions may depend
		# on these groups existing
		if groupadd_param and sysroot:
			bb.debug(1, "Running groupadd commands ...")
			# Invoke multiple instances of groupadd for parameter lists
			# separated by ';'
			param_list = groupadd_param.split(';')
			for opts in param_list:
				groupname = opts.split()[-1]
				with open(group_file, 'r') as f:
					passwd_lines = f.read()
				group_re = re.compile('\n%s' % groupname)
				if group_re.search(passwd_lines):
					bb.note("Note: groupname %s already exists, not re-creating it" % groupname)
					continue
				try:
					output, err = bb.process.run('groupadd %s %s' % (opt, opts))
				except bb.process.CmdError as exc:
					bb.error("Failed to add group: %s" % exc)
				else:
					bb.note("Successful to add group %s" % groupname)

		if useradd_param:
			bb.debug(1, "Running useradd commands ...")
			# Invoke multiple instances of useradd for parameter lists
			# separated by ';'
			param_list = useradd_param.split(';')
			for opts in param_list:
				# useradd does not have a -f option, so we have to check if the
				# username already exists manually
				username = opts.split()[-1]
				with open(user_file, 'r') as f:
					passwd_lines = f.read()
				user_re = re.compile('\n%s' % username)
				if user_re.search(passwd_lines):
					bb.note("Note: username %s already exists, not re-creating it" % username)
					continue
				try:
					output, err = bb.process.run('useradd %s %s' % (opt, opts))
				except bb.process.CmdError as exc:
					bb.error("Failed to add user: %s" % exc)
				else:
					bb.note("Successful to add user %s" % username)

fakeroot python useradd_sysroot () {
	useradd_preinst(d)
}

fakeroot python useradd_sysroot_sstate () {
    if d.getVar("BB_CURRENTTASK", True) == "package_setscene":
        useradd_preinst(d)
}


do_install[prefuncs] += "${SYSROOTFUNC}"
SYSROOTFUNC = "useradd_sysroot"
SYSROOTFUNC_virtclass-cross = ""
SYSROOTFUNC_virtclass-native = ""
SYSROOTFUNC_virtclass-nativesdk = ""
SSTATEPREINSTFUNCS += "${SYSROOTPOSTFUNC}"
SYSROOTPOSTFUNC = "useradd_sysroot_sstate"
SYSROOTPOSTFUNC_virtclass-cross = ""
SYSROOTPOSTFUNC_virtclass-native = ""
SYSROOTPOSTFUNC_virtclass-nativesdk = ""

USERADDSETSCENEDEPS = "base-passwd:do_populate_sysroot_setscene shadow-native:do_populate_sysroot_setscene ${MLPREFIX}shadow-sysroot:do_populate_sysroot_setscene"
USERADDSETSCENEDEPS_virtclass-cross = ""
USERADDSETSCENEDEPS_virtclass-native = ""
USERADDSETSCENEDEPS_virtclass-nativesdk = ""
do_package_setscene[depends] = "${USERADDSETSCENEDEPS}"

# Recipe parse-time sanity checks
def update_useradd_after_parse(d):
	useradd_packages = d.getVar('USERADD_PACKAGES', True)

	if not useradd_packages:
		raise bb.build.FuncFailed, "%s inherits useradd but doesn't set USERADD_PACKAGES" % d.getVar('FILE')

	for pkg in useradd_packages.split():
		if not d.getVar('USERADD_PARAM_%s' % pkg, True) and not d.getVar('GROUPADD_PARAM_%s' % pkg, True):
			raise bb.build.FuncFailed, "%s inherits useradd but doesn't set USERADD_PARAM or GROUPADD_PARAM for package %s" % (d.getVar('FILE'), pkg)

python __anonymous() {
	update_useradd_after_parse(d)
}

# Return a single [GROUP|USER]ADD_PARAM formatted string which includes the
# [group|user]add parameters for all USERADD_PACKAGES in this recipe
def get_all_cmd_params(d, cmd_type):
	import string
	
	param_type = cmd_type.upper() + "ADD_PARAM_%s"
	params = []

	useradd_packages = d.getVar('USERADD_PACKAGES', True) or ""
	for pkg in useradd_packages.split():
		param = d.getVar(param_type % pkg, True)
		if param:
			params.append(param)

	return string.join(params, "; ")

# Adds the preinst script into generated packages
fakeroot python populate_packages_prepend () {
	def update_useradd_package(pkg):
		bb.debug(1, 'adding user/group calls to preinst for %s' % pkg)

		"""
		useradd preinst is appended here because pkg_preinst may be
		required to execute on the target. Not doing so may cause
		useradd preinst to be invoked twice, causing unwanted warnings.
		"""
		preinst = d.getVar('pkg_preinst_%s' % pkg, True) or d.getVar('pkg_preinst', True)
		if not preinst:
			preinst = '#!/bin/sh\n'
		preinst += d.getVar('useradd_preinst', True)
		d.setVar('pkg_preinst_%s' % pkg, preinst)

		# RDEPENDS setup
		rdepends = d.getVar("RDEPENDS_%s" % pkg, True) or ""
		rdepends += ' ' + d.getVar('MLPREFIX') + 'base-passwd'
		rdepends += ' ' + d.getVar('MLPREFIX') + 'shadow'
		d.setVar("RDEPENDS_%s" % pkg, rdepends)

	# Add the user/group preinstall scripts and RDEPENDS requirements
	# to packages specified by USERADD_PACKAGES
	if not bb.data.inherits_class('nativesdk', d):
		useradd_packages = d.getVar('USERADD_PACKAGES', True) or ""
		for pkg in useradd_packages.split():
			update_useradd_package(pkg)
}

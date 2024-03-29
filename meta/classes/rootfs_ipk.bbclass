#
# Creates a root filesystem out of IPKs
#
# This rootfs can be mounted via root-nfs or it can be put into an cramfs/jffs etc.
# See image.bbclass for a usage of this.
#

EXTRAOPKGCONFIG ?= ""
ROOTFS_PKGMANAGE = "opkg opkg-collateral ${EXTRAOPKGCONFIG}"
ROOTFS_PKGMANAGE_BOOTSTRAP  = "run-postinsts"

do_rootfs[depends] += "opkg-native:do_populate_sysroot opkg-utils-native:do_populate_sysroot"
do_rootfs[recrdeptask] += "do_package_write_ipk"

do_rootfs[lockfiles] += "${WORKDIR}/ipk.lock"

IPKG_ARGS = "-f ${IPKGCONF_TARGET} -o ${IMAGE_ROOTFS} --force-overwrite --prefer-arch-to-version"
# The _POST version also works when constructing the matching SDK
IPKG_ARGS_POST = "-f ${IPKGCONF_TARGET} -o $INSTALL_ROOTFS_IPK --force-overwrite --prefer-arch-to-version"

OPKG_PREPROCESS_COMMANDS = "package_update_index_ipk; package_generate_ipkg_conf"

OPKG_POSTPROCESS_COMMANDS = "ipk_insert_feed_uris; "

opkglibdir = "${localstatedir}/lib/opkg"

# Which packages to not install on the basis of a recommendation
BAD_RECOMMENDATIONS ?= ""
MULTILIBRE_ALLOW_REP = "${opkglibdir}"

fakeroot rootfs_ipk_do_rootfs () {
	set -x

	rm -f ${IPKGCONF_TARGET}
	touch ${IPKGCONF_TARGET}

	${OPKG_PREPROCESS_COMMANDS}

	mkdir -p ${T}/
 
	STATUS=${IMAGE_ROOTFS}${opkglibdir}/status
	mkdir -p ${IMAGE_ROOTFS}${opkglibdir}

	opkg-cl ${IPKG_ARGS} update

	# prime the status file with bits that we don't want
	for i in ${BAD_RECOMMENDATIONS}; do
		pkginfo="`opkg-cl ${IPKG_ARGS} info $i`"
		if [ ! -z "$pkginfo" ]; then
			echo "$pkginfo" | grep -e '^Package:' -e '^Architecture:' -e '^Version:' >> $STATUS
			echo "Status: deinstall hold not-installed" >> $STATUS
			echo >> $STATUS
		else
			echo "Requested ignored recommendation $i is not a package"
		fi
	done

	#install
	export INSTALL_PACKAGES_ATTEMPTONLY_IPK="${PACKAGE_INSTALL_ATTEMPTONLY}"
	export INSTALL_PACKAGES_LINGUAS_IPK="${LINGUAS_INSTALL}"
	export INSTALL_TASK_IPK="rootfs"

	export INSTALL_ROOTFS_IPK="${IMAGE_ROOTFS}"
	export INSTALL_CONF_IPK="${IPKGCONF_TARGET}"
	export INSTALL_PACKAGES_IPK="${PACKAGE_INSTALL}"

	#post install
	export D=${IMAGE_ROOTFS}
	export OFFLINE_ROOT=${IMAGE_ROOTFS}
	export IPKG_OFFLINE_ROOT=${IMAGE_ROOTFS}
	export OPKG_OFFLINE_ROOT=${IPKG_OFFLINE_ROOT}

	package_install_internal_ipk

	# Distro specific packages should create this
	#mkdir -p ${IMAGE_ROOTFS}/etc/opkg/
	#grep "^arch" ${IPKGCONF_TARGET} >${IMAGE_ROOTFS}/etc/opkg/arch.conf

	rootfs_install_complementary

	${OPKG_POSTPROCESS_COMMANDS}
	${ROOTFS_POSTINSTALL_COMMAND}
	
	if ${@base_contains("IMAGE_FEATURES", "read-only-rootfs", "true", "false" ,d)}; then
		if grep Status:.install.ok.unpacked ${STATUS}; then
			echo "Some packages could not be configured offline and rootfs is read-only."
			exit 1
		fi
	fi

	install -d ${IMAGE_ROOTFS}/${sysconfdir}
	echo ${BUILDNAME} > ${IMAGE_ROOTFS}/${sysconfdir}/version

	${ROOTFS_POSTPROCESS_COMMAND}
	
	rm -f ${IMAGE_ROOTFS}${opkglibdir}/lists/*
	if ${@base_contains("IMAGE_FEATURES", "package-management", "false", "true", d)}; then
		if ! grep Status:.install.ok.unpacked ${STATUS}; then
			# All packages were successfully configured.
			# update-rc.d, base-passwd, run-postinsts are no further use, remove them now
			remove_run_postinsts=false
			if [ -e ${IMAGE_ROOTFS}${sysconfdir}/init.d/run-postinsts ]; then
				remove_run_postinsts=true
			fi
			opkg-cl ${IPKG_ARGS} --force-depends remove update-rc.d base-passwd ${ROOTFS_BOOTSTRAP_INSTALL} || true

			# Need to remove rc.d files for run-postinsts by hand since opkg won't
			# call postrm scripts in offline root mode.
			if $remove_run_postinsts; then
				update-rc.d -f -r ${IMAGE_ROOTFS} run-postinsts remove
			fi

			# Also delete the status files
			remove_packaging_data_files
		fi
	fi
	set +x
	log_check rootfs
}

rootfs_ipk_write_manifest() {
	manifest=${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.rootfs.manifest
	cp ${IMAGE_ROOTFS}${opkglibdir}/status $manifest

	sed '/Depends/d' -i $manifest
	sed '/Status/d' -i $manifest
	sed '/Architecture/d' -i $manifest
	sed '/Installed-Time/d' -i $manifest
	sed '/Auto-Installed/d' -i $manifest
	sed '/Recommends/d' -i $manifest
	sed '/Provides/d' -i $manifest
	sed '/Conflicts/d' -i $manifest
}

remove_packaging_data_files() {
	rm -rf ${IMAGE_ROOTFS}${opkglibdir}
	# We need the directory for the package manager lock
	mkdir ${IMAGE_ROOTFS}${opkglibdir}
}

list_installed_packages() {
	if [ "$1" = "arch" ] ; then
		opkg-cl ${IPKG_ARGS_POST} status | opkg-query-helper.py -a
	elif [ "$1" = "file" ] ; then
		opkg-cl ${IPKG_ARGS_POST} status | opkg-query-helper.py -f | while read pkg pkgfile
		do
			fullpath=`find ${DEPLOY_DIR_IPK} -name "$pkgfile" || true`
			if [ "$fullpath" = "" ] ; then
				echo "$pkg $pkgfile"
			else
				echo "$pkg $fullpath"
			fi
		done
	else
		opkg-cl ${IPKG_ARGS_POST} list_installed | awk '{ print $1 }'
	fi
}

rootfs_list_installed_depends() {
	opkg-cl ${IPKG_ARGS_POST} status | opkg-query-helper.py
}

rootfs_install_packages() {
	opkg-cl ${IPKG_ARGS_POST} install `cat $1`
}

ipk_insert_feed_uris () {

	echo "Building from feeds activated!"

	for line in ${IPK_FEED_URIS}
	do
		# strip leading and trailing spaces/tabs, then split into name and uri
		line_clean="`echo "$line"|sed 's/^[ \t]*//;s/[ \t]*$//'`"
		feed_name="`echo "$line_clean" | sed -n 's/\(.*\)##\(.*\)/\1/p'`"
		feed_uri="`echo "$line_clean" | sed -n 's/\(.*\)##\(.*\)/\2/p'`"

		echo "Added $feed_name feed with URL $feed_uri"

		# insert new feed-sources
		echo "src/gz $feed_name $feed_uri" >> ${IPKGCONF_TARGET}
	done

	# Allow to use package deploy directory contents as quick devel-testing
	# feed. This creates individual feed configs for each arch subdir of those
	# specified as compatible for the current machine.
	# NOTE: Development-helper feature, NOT a full-fledged feed.
	if [ -n "${FEED_DEPLOYDIR_BASE_URI}" ]; then
		for arch in ${PACKAGE_ARCHS}
		do
			echo "src/gz local-$arch ${FEED_DEPLOYDIR_BASE_URI}/$arch" >> ${IMAGE_ROOTFS}/etc/opkg/local-$arch-feed.conf
	    done
	fi
}

python () {

    if d.getVar('BUILD_IMAGES_FROM_FEEDS', True):
        flags = d.getVarFlag('do_rootfs', 'recrdeptask')
        flags = flags.replace("do_package_write_ipk", "")
        flags = flags.replace("do_deploy", "")
        flags = flags.replace("do_populate_sysroot", "")
        d.setVarFlag('do_rootfs', 'recrdeptask', flags)
        d.setVar('OPKG_PREPROCESS_COMMANDS', "package_generate_archlist\nipk_insert_feed_uris")
        d.setVar('OPKG_POSTPROCESS_COMMANDS', '')
}


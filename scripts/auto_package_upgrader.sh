#!/bin/bash
#
# Copyright (c) 2012 Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# DESCRIPTION
# This script will attempt to automatically upgrade the packages given in
# the input file. The file format is as follows:
#
# package_name,current_version,new_version,email_address
#
# TODO: add support for git and svn
#
# AUTHORS
# Laurentiu Palcu <laurentiu.palcu@intel.com>
#


PU_LIST_FN="`pwd`/package_upgrade_list.txt"

# # - simple comment
# ~ - upgrade successful
# ! - upgrade failed, unknown reason
# @ - upgrade failed, licence checksum
# % - upgrade failed, fetch problem
# & - upgrade not done, SRC_URI not supported
PU_LIST=`cat ${PU_LIST_FN}|grep -v -e "^#" -e "^\!" -e "^@" -e "^~" -e "^%" -e "^&"`

APU_DIR="/ssd/yocto/APU"
POKY_DIR="$APU_DIR/poky"
BUILD_DIR="$APU_DIR/build"
LOG_DIR="$APU_DIR/log"
DOWNLOADS_DIR="/ssd/yocto/downloads"
SSTATE_CACHE_DIR="/ssd/yocto/sstate-cache"

USE_DOWNLOADS_DIR="yes"
USE_SSTATE_CACHE_DIR="no"
DELETE_PREVIOUS_BUILD_DIR="no"
DELETE_PACKAGE_OBJECTS_AFTER_BUILD="yes"
DELETE_PREVIOUS_LOG_DIR="yes"
SEND_MAIL="yes"

MACHINES="qemux86 qemux86-64 qemuarm qemumips qemuppc"

FETCH_STATUS_LINE="+----------+----------------------+------------------------+"
FETCH_STATUS_HEADER="| original | new_ver_no_checksums | new_ver_with_checksums |"
COMPILE_STATUS_LINE="+---------+------------+---------+----------+---------+"
COMPILE_STATUS_HEADER="| qemux86 | qemux86-64 | qemuarm | qemumips | qemuppc |"

function send-mail() {
	if [ "$SEND_MAIL" == "yes" ]; then
		mutt $@
	fi
}

function success_message() {
	echo -e "Hi,\n"
	echo -e "This is to let you know that the *${PN}* package has been automatically\n"\
			"updated from ${PCV} to ${PNV}. Before submitting the attached patch, make\n"\
			"sure you test it.\n"
	echo -e "The package has been successfully built on all architectures. Compilation\n"\
			"logs are also attached.\n"
	echo -e "The commit upon which the patches were applied was: $(echo $last_commit|cut -d' ' -f2)\n"
	echo -e "Next steps:"
	echo -e "    - apply the patch: git am <patch_name>"
	echo -e "    - compile an image that contains the package"
	echo -e "    - perform some basic sanity tests"
	echo -e "    - amend the patch and sign it off: git commit -s --reset-author --amend"
	echo -e "    - send it to the list\n"
	echo -e "*** This message was sent automatically, DO NOT REPLY! ***"
}

function fail_message() {
	echo -e "Hi,\n"
	echo -e "This is to let you know that *${PN}* package coulnd not be automatically upgraded"\
			"from ${PCV} to ${PNV}.\n"
	if [ "$1" == "compile" ]; then
		echo -e "Error: *Compilation failed* for at least one of the architectures.\n"
		echo -e "Attached are the compilation logs, for your reference!\n"
		echo -e "The commit upon which the patches were applied was: $(echo $last_commit|cut -d' ' -f2)\n"
		echo -e "${COMPILE_STATUS_LINE}\n${COMPILE_STATUS_HEADER}\n${COMPILE_STATUS_LINE}"
		printf "| %7s | %10s | %7s | %8s | %7s |\n" $compile_status
		echo -e "${COMPILE_STATUS_LINE}\n"
		echo -e "Legend:"
		echo -e "OK      - compilation successful"
		echo -e "FAIL(I) - incompatible host"
		echo -e "FAIL(L) - licence issue"
		echo -e "FAIL(P) - patches do not apply"
		echo -e "N/A     - compilation not done\n"
	else
		echo -e "Error: *Fetch failed*.\n"
		echo -e "${FETCH_STATUS_LINE}\n${FETCH_STATUS_HEADER}\n${FETCH_STATUS_LINE}"
		printf "| %8s | %20s | %22s |\n" $fetch_status
		echo -e "${FETCH_STATUS_LINE}\n"
		echo -e "Legend:"
		echo -e "OK       - fetch successful"
		echo -e "FAIL(CS) - fetch failed due to checksums mismatch (normal behavior)"
		echo -e "N/A      - fetch not done\n"
	fi
	echo -e "*** This message was sent automatically, DO NOT REPLY! ***"
}

function setup_bitbake() {
	cd $APU_DIR

	if [ "$DELETE_PREVIOUS_BUILD_DIR" == "yes" ]; then
		echo -n "> deleting previous build directory..."
		rm -rf $BUILD_DIR >/dev/null 2>&1 && echo OK
	fi

	echo -n "> setup bitbake environment..."
	. poky/oe-init-build-env >/dev/null 2>&1 && echo OK

	# we are in build directory now

	# change number of threads to 8
	sed -i -e "s/#BB_NUMBER_THREADS\(.*\)$/BB_NUMBER_THREADS = \"8\"/" -e "s/#PARALLEL_MAKE\(.*\)$/PARALLEL_MAKE = \"-j 8\"/" ./conf/local.conf

	# use other downloads dir, if requested
	if [ "$USE_DOWNLOADS_DIR" == "yes" ]; then
		sed -i -e "s@#DL_DIR ?= \"\(.*\)\"@DL_DIR ?= \"${DOWNLOADS_DIR}\"@" ./conf/local.conf
	fi

	# use other SSTATE_CACHE directory, if requested
	if [ "$USE_SSTATE_CACHE_DIR" == "yes" ]; then
		sed -i -e "s@#SSTATE_DIR ?= \"\(.*\)\"@SSTATE_DIR ?= \"${SSTATE_CACHE_DIR}\"@" ./conf/local.conf
	fi

	# delete package objects after build, to save disk space
	if [ "$DELETE_PACKAGE_OBJECTS_AFTER_BUILD" == "yes" ]; then
		inherit=`cat ./conf/local.conf|grep "INHERIT"|sed -e "s/INHERIT += \"\(.*\)\"/\1/"`
		if [ "$inherit" == "" ]; then
			echo "INHERIT += \"rm_work\"" >> ./conf/local.conf
		fi
	else
		sed -i -e "/INHERIT += \"\(.*\)\"/d" ./conf/local.conf
	fi
}

function checkout_upgrades_branch() {
	cd $POKY_DIR
	current_branch=`git status|grep "^# On branch "|sed -e 's/^# On branch \(.*\)/\1/'`

	if [ "$current_branch" == "upgrades" ]; then
		# we commit all changes (because it's easier to delete the branch this way)
		git commit -a -m "to be discarded" >/dev/null 2>&1
		git checkout master >/dev/null 2>&1
		git branch -D upgrades >/dev/null 2>&1
	else
		git branch -D upgrades >/dev/null 2>&1
	fi

	echo -n "> checkout master branch, update and create "upgrades" branch..."
	git checkout master >/dev/null 2>&1 &&\
	git pull >/dev/null 2>&1 &&\
	git checkout -b upgrades >/dev/null 2>&1

	if [ $? != 0 ]; then
		echo "> git operations failed, exit!"
		exit 1
	else
		echo OK
	fi

	last_commit=$(git log|head -n1)
}

function show_last_commit() {
	cd $POKY_DIR
	git show master|grep "^commit"|cut -d' ' -f2
}

function discard_changes() {
	cd $POKY_DIR
	git commit -a -m "discard" >/dev/null 2>&1 && git reset --hard HEAD~1 >/dev/null 2>&1
}

# Function: creates a licence diff
# Arguments:
#	$1 - package name $PN
#	$2 - old package version $PCV
#	$3 - new package version $PNV
#	$4 - uri type and file (Ex: http|some_site/${BPN}-${PV}.tar.gz)
#	$5 - offending licence file
function create_licence_diff() {
	cd $LOG_DIR
	mkdir licence_$PN
	cd licence_$PN

	old_archive_path=$(echo $4|cut -d'|' -f2)
	old_archive=${old_archive_path##*/}
	archive_type=${old_archive##*.}

	# we only change the version to find the new archive name
	new_archive=$(echo $old_archive|sed -e "s/$2/$3/")

	cp ${DOWNLOADS_DIR}/$old_archive ${DOWNLOADS_DIR}/$new_archive ./ || return 1

	# extract the archives and get the directory names from archives (we could
	# guess it from the archive name but we never now. This seems safer.
	old_ver_dir=""
	new_ver_dir=""
	case "$archive_type" in
		"tgz") ;&
		"gz")
			old_ver_dir=$(tar tzf $old_archive|head -n1)
			tar xzf $old_archive
			new_ver_dir=$(tar tzf $new_archive|head -n1)
			tar xzf $new_archive
			;;
		"bz2")
			old_ver_dir=$(tar tjf $old_archive|head -n1)
			tar xjf $old_archive
			new_ver_dir=$(tar tjf $new_archive|head -n1)
			tar xjf $new_archive
			;;
		"zip")
			# TODO
			return 1
			unzip $old_archive
			unzip $new_archive
			;;
		"xz")
			# TODO
			return 1
			;;
		*)
			;;
	esac

	if [ -a "$old_ver_dir/$5" -a -a "$new_ver_dir/$5" ]; then
		diff -u $old_ver_dir/$5 $new_ver_dir/$5
		return 0
	fi

	return 1
}

function send_licence_fail_mail() {

	offending_licence_file=`cat $LOG_DIR/compile_${1}_$machine.log |grep "md5 data is not matching for file"|sed -e "s/\(.*\)file:\/\/\([^;]*\);\(.*\)/\2/"`
	create_licence_diff $1 $2 $3 $6 $offending_licence_file > $LOG_DIR/licence_${1}-${2}_vs_${3}.diff || return 1

	new_licence_md5=`cat $LOG_DIR/compile_${1}_$machine.log |grep "ERROR: \(.*\) The new md5 checksum is"|sed -e "s/ERROR: \(.*\) The new md5 checksum is \(.*\)/\2/"`

	licence_message=\
"Hi,\n
The package $1 could not be automatically upgraded from $2 to $3.
The main reason is licence checksum fail. Below are the new checksums
and attached is a diff between the old licence file and new one.\n
SRC_URI[md5sum] = \"$4\"
SRC_URI[sha256sum] = \"$5\"
licence file: $offending_licence_file
licence file new md5 sum: $new_licence_md5

*** This mail was automatically send. DO NOT REPLY! ***"

	echo -e "$licence_message" | mutt -s "[APU] ${1}: upgrading to ${3} failed due to licence change" -c laurentiu.palcu@linux.intel.com -a $LOG_DIR/licence_${1}-${2}_vs_${3}.diff -- $7
}

function get_the_recipe_path() {
	cd $POKY_DIR
	current_recipe_name=`find . -name "${1}_${2}.bb"`
	if [ "$current_recipe_name" != "" ]; then
		echo "${current_recipe_name%/*}"
	fi
}

# check if the protocol used to fetch the package is http/ftp. Reject git/svn for now.
function validate_src_uri() {
	src_uri=$(bb_env $1|grep "^SRC_URI")
	cd $POKY_DIR
#[lp]	recipe=$(cat $1/${2}_${3}.bb)
	uri_type_and_file=$(echo $src_uri|\
			sed -e "s/\(.*\)SRC_URI\( *\)=\( *\)\"\( *\)\(http\|https\|ftp\|git\|svn\):\/\/\([^ \"]*\)\(.*\)/\5\|\6/"\
				-e "s/\(.*\)SRC_URI\( *\)=\( *\)\"\( *\)\${\(DEBIAN_MIRROR\|KERNELORG_MIRROR\|GNU_MIRROR\|SOURCEFORGE_MIRROR\|GNOME_MIRROR\|APACHE_MIRROR\|XORG_MIRROR\|GPE_MIRROR\)}\/\([^ \"]*\)\(.*\)/\5\|\6/")
	uri_type=$(echo $uri_type_and_file|cut -d'|' -f1)

	case $uri_type in
		"https") ;&
		"http") ;&
		"ftp") ;&
		"SOURCEFORGE_MIRROR") ;&
		"DEBIAN_MIRROR") ;&
		"GNU_MIRROR") ;&
		"GNOME_MIRROR") ;&
		"APACHE_MIRROR") ;&
		"GPE_MIRROR") ;&
		"XORG_MIRROR") ;&
		"KERNELORG_MIRROR")
			echo $uri_type_and_file
			return 0
		;;

		*)
			return 1
		;;
	esac
}

# Function: retrieve the environment
# Arguments:
#	$1 - package name
function bb_env() {
	cd $BUILD_DIR
	bitbake -e $1
}

# Function: performs a bitbake fetch
# Arguments:
# $1 - package name
# $2 - package version (used only for printing info)
# $3 - a number to distinguish between different fetch logs:
#		Values:
#			0 - original package fetch
#			1 - new version fetch (before changing the checksums)
#			2 - the last fetch (after fixing the checksums)
# $4 - whether to perform a cleanall before or not. If it's missing
#	   no cleanall will be performed
#		Values:
#			cleanall - perform cleanall before fetch
function bb_fetch() {
	cd $BUILD_DIR

	if [ "$4" == "cleanall" ]; then
		echo -n "> $1: cleaning all..."
		bitbake -c cleanall $1 >/dev/null 2>&1
		echo "OK"
	fi

	echo -n "> $1: fetching ver. $2..."
	ln -sf $LOG_DIR/fetch_${1}_${3}.log ${LOG_DIR}/log
	bitbake -c fetch $1 > $LOG_DIR/fetch_${1}_${3}.log 2>&1
	if [ $? -ne 0 ]; then
		echo "FAIL"
		return 1
	fi

	echo "OK"
	return 0
}

# Function: checks the compilation log to find out the failure reason
# Arguments:
#	$1 - package name
#	$2 - machine: qemux86, qemux86-64, qemuarm, qemumips, qemuppc
function get_compile_fail_reason() {
	not_compatible_with_host=`cat $LOG_DIR/compile_${1}_${2}.log|grep "^ERROR: ${PN} was skipped: incompatible with host"`
	if [ "$not_compatible_with_host" != "" ]; then
		return 0
	fi

	if [ "`cat $LOG_DIR/compile_${1}_${2}.log|grep \"ERROR: Licensing Error\"`" != "" ]; then
		return 1
	fi

	if [ "`cat $LOG_DIR/compile_${1}_${2}.log | grep \"ERROR: Function failed: patch_do_patch\"`" != "" ]; then
		return 2
	fi

	return 3
}

# Function: compiles a certain package
# Arguments:
#	$1 - package name
#	$2 - machine: qemux86, qemux86-64, qemuarm, qemumips, qemuppc
function bb_compile() {
	echo -n "> $1/$2: cleaning all..."
	MACHINE=$2 bitbake -c cleanall $1 >/dev/null 2>&1
	echo OK
	echo -n "> $1/$2: compiling..."
	ln -sf $LOG_DIR/compile_${PN}_${2}.log ${LOG_DIR}/log
	MACHINE=$2 bitbake $1 > $LOG_DIR/compile_${PN}_${2}.log 2>&1
	if [ $? -ne 0 ]; then
		get_compile_fail_reason $1 $2
		case "$?" in
			"0")
				echo "FAIL(INCOMPATIBLE HOST)"
				return 1
				;;
			"1")
				echo "FAIL(LICENCE CHECKSUM FAILED)"
				return 2
				;;
			"2")
				echo "FAIL(PATCHES DO NOT APPLY CLEAN)"
				return 3
				;;
			*)
				echo "FAIL"
				return 4
				;;
		esac
	fi

	echo "OK"
	return 0
}

# Function: replaces the checksums in the recipe and resets PR
# Arguments:
#	$1 - package name
#	$2 - package version
#	$3 - recipe path
function fix_recipe_checksums() {
	MD5s="`cat ${LOG_DIR}/fetch_${1}_1.log |\
			grep -e "File: '\(.*\)' has md5 checksum \(.*\) when \(.*\) was expected"|uniq|\
			sed -e "s/File: '\(.*\)' has md5 checksum \(.*\) when \(.*\) was expected/\2,\3/"`"
	SHA256s="`cat ${LOG_DIR}/fetch_${1}_1.log |\
			grep -e "File: '\(.*\)' has sha256 checksum \(.*\) when \(.*\) was expected"|uniq|\
			sed -e "s/File: '\(.*\)' has sha256 checksum \(.*\) when \(.*\) was expected/\2,\3/"`"

	old_md5=`echo $MD5s|cut -d',' -f2`
	new_md5=`echo $MD5s|cut -d',' -f1`
	old_sha256=`echo $SHA256s|cut -d',' -f2`
	new_sha256=`echo $SHA256s|cut -d',' -f1`

	if [ "$old_md5" == "" ]; then
		return 1
	fi

	echo "> $1: change checksums and reset PR"
	# change checksums
	sed -i -e "s/SRC_URI\[md5sum\]\( *\)=\( *\)\"\(.*\)\"/SRC_URI\[md5sum\] = \"${new_md5}\"/" $POKY_DIR/${3}/${1}_${2}.bb
	sed -i -e "s/SRC_URI\[sha256sum\]\( *\)=\( *\)\"\(.*\)\"/SRC_URI\[sha256sum\] = \"${new_sha256}\"/" $POKY_DIR/${3}/${1}_${2}.bb

	# PR reset
	sed -i -e "s/PR\( *\)=\( *\)\"\${INC_PR}.\([0-9]*\)\"/PR = \"\${INC_PR}.0\"/" -e "s/PR\( *\)=\( *\)\"r\([0-9]*\)\"/PR = \"r0\"/" $POKY_DIR/${3}/${1}_${2}.bb

	return 0
}

function archive_logs() {
	# archive the compilation logs, for reference
	echo -n "> $PN: archiving logs..."
	cd $LOG_DIR
	tar cjf logs_${PN}_${PCV}_${PNV}.tar.bz2 *_${PN}_*.log >/dev/null 2>&1
	echo OK
}

function send_fetch_fail_message() {
	archive_logs
	echo -n "> $PN: sending mail to maintainer($MAINTAINER_MAIL)..."
	fail_message fetch | mutt -s "[APU] $PN: Automatic upgrade to $PNV FAILED" -c "laurentiu.palcu@linux.intel.com" -a $LOG_DIR/logs_${PN}_${PCV}_${PNV}.tar.bz2 -- $MAINTAINER_MAIL && echo OK
}

function commit_the_changes() {
	cd $POKY_DIR
	echo -n "> $PN: commiting changes..."
	git commit -a --author="Auto Package Upgrade <apu@not.set>" -m "${PN}: upgrade to ${PNV}" >/dev/null 2>&1 && echo OK
	echo -n "> $PN: formatting patch..."
	patch_file=$(git format-patch -M -1)
	echo OK
}

function upgrade_package() {
	PN=`echo $1|cut -d',' -f1`
	PCV=`echo $1|cut -d',' -f2`
	PNV=`echo $1|cut -d',' -f3`
	MAINTAINER_MAIL=`echo $1|cut -d',' -f4`

	echo "*** Upgrading $PN : $PCV -> $PNV ***"

	# any uncommited changes in the tree will be discarded
	discard_changes

	recipe_path=$(get_the_recipe_path $PN $PCV)
	if [ "$recipe_path" == "" ]; then
		echo "*** Could not find recipe ${PN}_${PCV}.bb, upgrade already done? Moving to next package! ***"
		return
	fi

	uri_type_and_file=$(validate_src_uri $PN)
	if [ $? -ne 0 ]; then
		echo "*** SRC_URI not supported yet. Do the upgrade manually! ***"
		sed -i -e "s/^${PN}/\&${PN}/" $PU_LIST_FN
		return
	fi


	bb_fetch $PN $PCV 0
	if [ $? -ne 0 ]; then
		fetch_status="FAIL N/A N/A"
		send_fetch_fail_message
		echo "*** Fetching the original version FAILED. Must be a network problem... ***"
		return
	fi

	cd $POKY_DIR
	git mv ${recipe_path}/${PN}_${PCV}.bb ${recipe_path}/${PN}_${PNV}.bb

	if [ -e ${recipe_path}/${PN}-native_${PCV}.bb ]; then
		git mv ${recipe_path}/${PN}-native_${PCV}.bb ${recipe_path}/${PN}-native_${PNV}.bb
	fi

	if [ -e ${recipe_path}/${PN}-nativesdk_${PCV}.bb ]; then
		git mv ${recipe_path}/${PN}-nativesdk_${PCV}.bb ${recipe_path}/${PN}-nativesdk_${PNV}.bb
	fi

	# if there is a directory with patches, change the version of the directory too
	if [ -d ${recipe_path}/${PN}_${PCV} ]; then
		git mv ${recipe_path}/${PN}_${PCV} ${recipe_path}/${PN}_${PNV}
	elif [ -d ${recipe_path}/${PN}-${PCV} ]; then
		git mv ${recipe_path}/${PN}-${PCV} ${recipe_path}/${PN}-${PNV}
	fi

	# first fetch after incrementing the version should fail, get the new checksums, replace the old ones and reset PR
	bb_fetch $PN $PNV 1 cleanall
	if [ $? -ne 0 ]; then
		fix_recipe_checksums $PN $PNV $recipe_path
		if [ $? -ne 0 ]; then
			fetch_status="OK FAIL N/A"
			send_fetch_fail_message
			echo "*** Fetching version $PNV of package $PN FAILED from unknown reason!!! Please upgrade manually! ***"
			sed -i -e "s/^${PN}/%${PN}/" $PU_LIST_FN
			return
		fi
	else
		fetch_status="OK OK?!? N/A"
		send_fetch_fail_message
		echo "*** Fetching version $PNV of package $PN SUCCEEDED without changing the checksums!!! Please upgrade manually! ***"
		sed -i -e "s/^${PN}/%${PN}/" $PU_LIST_FN
		return
	fi

	# this fetch should succeed
	bb_fetch $PN $PNV 2 cleanall
	if [ $? -ne 0 ]; then
		fetch_status="OK FAIL(CS) FAIL"
		send_fetch_fail_message
		echo "*** Fetching the package $PN FAILED, please upgrade manually ***"
		sed -i -e "s/^${PN}/%${PN}/" $PU_LIST_FN
		return
	fi

	# build for all architectures
	compile_status=""
	compile_failed=0
	for machine in $MACHINES; do
		bb_compile $PN $machine
		case "$?" in
			"0") ;;
			"1")
				compile_status=$(echo $compile_status FAIL\(I\))
				;;
			"2")
				compile_status="FAIL(L) N/A N/A N/A N/A"
				send_licence_fail_mail $PN $PCV $PNV $new_md5 $new_sha256 $uri_type_and_file $MAINTAINER_MAIL ||\
					echo "> Licence diff mail NOT sent due to problems..."
				sed -i -e "s/^${PN}/@${PN}/" $PU_LIST_FN
				echo "*** Upgrading $PN FAILED: LICENCE ISSUE ****"
				return
				;;
			"3")
				compile_failed=1
				compile_status=$(echo $compile_status FAIL\(P\))
				;;
			*)
				compile_failed=1
				compile_status=$(echo $compile_status FAIL)
				;;
		esac
	done

	exit_if_forced

	archive_logs

	# commit the changes even if compilation failed, so we can send the patch
	commit_the_changes

	# if the package failed to compile on, at least, one machine, report it as failed
	if [ $compile_failed -eq 1 ]; then
		echo -n "> $PN: sending mail to maintainer($MAINTAINER_MAIL)..."
		fail_message compile |\
			mutt -s "[APU] $PN: Automatic upgrade to $PNV FAILED" -c "laurentiu.palcu@linux.intel.com" -a $POKY_DIR/$patch_file $LOG_DIR/logs_${PN}_${PCV}_${PNV}.tar.bz2 -- $MAINTAINER_MAIL && echo OK
		sed -i -e "s/^${PN}/!${PN}/" $PU_LIST_FN
		echo "*** Upgrade of $PN FAILED. Compilation issues, Please, do it manually! ***"

		# reset the changes because it will break future builds
		cd $POKY_DIR
		git reset --hard HEAD~1 >/dev/null 2>&1
		return
	fi

	# send mail to maintainer
	echo -n "> $PN: sending mail to maintainer($MAINTAINER_MAIL)..."
	success_message |\
		mutt -s "[APU] $PN: successfully upgraded to $PNV" -c "laurentiu.palcu@linux.intel.com" -a $POKY_DIR/$patch_file $LOG_DIR/logs_${PN}_${PCV}_${PNV}.tar.bz2 -- $MAINTAINER_MAIL && echo OK

	#delete the patch file
	cd $POKY_DIR
	rm "$patch_file"

	sed -i -e "s/^${PN}/~${PN}/" $PU_LIST_FN
	echo "*** Upgrading $PN from $PCV to $PNV was successful, please DO the tests! ***"
}

function get_maintainer_list() {
	cat $PU_LIST_FN|cut -d',' -f4|sort|uniq|sed -e "/^$/d"
}

# This function will exit the script if the STOP file exists in the APU_DIR.
# Useful when one wants to stop the script but let the current upgrade process finish.
function exit_if_forced() {
	if [ -e "${APU_DIR}/STOP" ]; then
		echo "############### FORCE STOP #################"
		rm ${APU_DIR}/STOP
		exit 1
	fi
}


# MAIN
if [ "$DELETE_PREVIOUS_LOG_DIR" == "yes" ]; then
	rm -rf $LOG_DIR
fi

if [ ! -d $LOG_DIR ]; then
	mkdir $LOG_DIR
fi

checkout_upgrades_branch

setup_bitbake

for p in $PU_LIST; do
	upgrade_package $p
	exit_if_forced
done

echo "### THE END ###"

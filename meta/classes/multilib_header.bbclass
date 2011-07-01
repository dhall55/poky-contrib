inherit siteinfo

export SITEINFO_BITS

#
# This routine will allow someone to specify a list of headers that need to be
# wrapped in a way that the bitsize of the target will be used to determine
# which header to use.
#
# TODO: mips64 n32 is not yet recognized in this code
# The check should be if the arch is mips64 and the bitsize is 32.
# then the siteinfo_bits should be set to "n32".
#
oe_multilib_header() {
	for each_header in "$@" ; do
	   if [ ! -f "${D}/${includedir}/$each_header" ]; then
	      bberror "oe_multilib_header: Unable to find header $each_header."
	      continue
	   fi
	   stem=$(echo $each_header | sed 's#\.h$##')
	   mv ${D}/${includedir}/$each_header ${D}/${includedir}/${stem}-${SITEINFO_BITS}.h

	   sed -e "s#ENTER_HEADER_FILENAME_HERE#${stem}#g" ${COREBASE}/scripts/multilib_header_wrapper.h > ${D}/${includedir}/$each_header
	done
}

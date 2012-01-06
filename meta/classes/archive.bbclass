# Archive the patched sources and build scripts to assist in license
# compliance by the end user or legal departments.

ARCHIVE_DIR = "${TMPDIR}/archives/${MULTIMACH_TARGET_SYS}/"
do_archive[dirs] = "${ARCHIVE_DIR}"

archive_do_archive() {
    # In mostly scenarios the $S is under $WORKDIR and has a separate
    # dir for storing the sources; but sometimes we also put the same
    # sources 'tmp/work-shared/' for sharing between different build.
    if [ -d ${S} -a ${S} != ${WORKDIR} ]; then
        sources_shared="0"

        if echo ${S} | grep "${TMPDIR}/work-shared" > /dev/null; then
            sources_shared="1"
        fi

        if [ x$sources_shared == "x1" ]; then
            # Create temporary sources directory
            mkdir -p ${PF}/temp
            cp -r ${S} ${PF}
            cp -r ${S}/../temp/* ${PF}/temp
            cp -r ${WORKDIR}/temp/* ${PF}/temp
            tarbase=`pwd`
            sourcedir=`basename ${S}`
        else
            tarbase=`dirname ${WORKDIR}`
            sourcedir=`echo ${S}|sed -e "s#${WORKDIR}/*##g"`
        fi

        tar -C $tarbase -cjf ${PF}.tar.bz2 ${PF}/$sourcedir \
            ${PF}/temp --exclude log.do_*

        # Remove the temporary sources directory
        if [ x$sources_shared == "x1" -a -d ${PF} ]; then
            rm -rf ${PF}
        fi
    fi

    # Just archive whole build directory up when $S is equal to $WORKDIR
    if [ -d ${S} -a ${S} == ${WORKDIR} ]; then
        tarbase=`dirname ${WORKDIR}`
        tar -C $tarbase -cjf ${PF}.tar.bz2 ${PF} --exclude log.do_*
    fi
}

addtask do_archive after do_patch before do_configure

EXPORT_FUNCTIONS do_archive

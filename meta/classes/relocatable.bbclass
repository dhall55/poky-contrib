SYSROOT_PREPROCESS_FUNCS += "relocatable_sysroot_preprocess"
PACKAGE_PREPROCESS_FUNCS += "relocatable_package_preprocess"

ELFEDIT_BIN ?= "chrpath"
ELFEDIT_LIST ?= "-l"
ELFEDIT_SET ?= "-r"
PREPROCESS_RELOCATE_DIRS ?= ""

# Recursively process 'directory' and modify the RPATH of child binaries
def process_dir (directory, d):
    import oe.process
    import stat

    cmd = d.expand('${ELFEDIT_BIN}')
    listarg = d.getVar('ELFEDIT_LIST')
    setarg = d.getVar('ELFEDIT_SET')
    tmpdir = d.getVar('TMPDIR')
    basedir = d.expand('${base_prefix}')

    #bb.debug(2, "Checking %s for binaries to process" % directory)
    if not os.path.exists(directory):
        return

    dirs = os.listdir(directory)
    for file in dirs:
        fpath = directory + "/" + file
        fpath = os.path.normpath(fpath)
        if os.path.islink(fpath):
            # Skip symlinks
            continue

        if os.path.isdir(fpath):
            process_dir(fpath, d)
        else:
            #bb.debug(2, "Testing %s for relocatability" % fpath)

            # We need read and write permissions for chrpath, if we don't have
            # them then set them temporarily. Take a copy of the files
            # permissions so that we can restore them afterwards.
            perms = os.stat(fpath)[stat.ST_MODE]
            if os.access(fpath, os.W_OK|os.R_OK):
                perms = None
            else:
                # Temporarily make the file writeable so we can chrpath it
                os.chmod(fpath, perms|stat.S_IRWXU)

            try:
                out = oe.process.run([cmd, listarg, fpath])
            except oe.process.ExecutionError as err:
                #bb.debug(1, "Failed to read RPATH of %s with error %s" % (fpath, str(err)))
                continue

            # Throw away everything other than the rpath list
            curr_rpath = out.partition("RPATH=")[2]
            #bb.debug(2, "Current rpath of %s is %s" % (fpath, curr_rpath.strip()))
            rpaths = curr_rpath.split(":")
            new_rpaths = []
            for rpath in rpaths:
                # If rpath is already dynamic skip processing
                if rpath.find("$ORIGIN") != -1:
                    #bb.debug(1, "RPATH already dynamic, not setting")
                    continue
                # If the rpath shares a root with base_prefix determine a new
                # dynamic rpath from the base_prefix shared root
                if rpath.find(basedir) != -1:
                    #bb.debug(2, "Setting ORIGIN from %s" % basedir)
                    depth = fpath.partition(basedir)[2].count('/')
                    libpath = rpath.partition(basedir)[2].strip()
                # Otherwise (i.e. cross packages) determine a shared root based
                # on the TMPDIR. NOTE: This will *not* work reliably for cross
                # packages, particularly in the case where your TMPDIR is a
                # short path (i.e. /usr/poky) as chrpath cannot insert an
                # rpath longer than that which is already set.
                else:
                    #bb.debug(2, "Setting ORIGIN from %s" % tmpdir)
                    depth = fpath.rpartition(tmpdir)[2].count('/')
                    libpath = rpath.partition(tmpdir)[2].strip()

                base = "$ORIGIN"
                while depth > 1:
                    base += "/.."
                    depth-=1
                new_rpaths.append("%s%s" % (base, libpath))

            # if we have modified some rpaths call chrpath to update the binary
            if len(new_rpaths):
                args = ":".join(new_rpaths)
                #bb.debug(2, "Setting rpath for %s to %s" %(fpath, args))
                try:
                    oe.process.run([cmd, setarg, args, fpath])
                except oe.process.ExecutionError as err:
                    bb.warn("Unable to set relocatable RPATH for %s with message '%s'" % (fpath, str(err)))

            # Reset the permissions if we had to change them
            if perms:
                os.chmod(fpath, perms)

# Iterate all children of 'path' which are likely to contain binary
# files and call process_dir on each directory
def rpath_replace (path, d):
    bindirs = d.expand("${bindir} ${sbindir} ${base_sbindir} ${base_bindir} ${libdir} ${base_libdir} ${libexecdir} ${PREPROCESS_RELOCATE_DIRS}").split()

    for bindir in bindirs:
        #bb.debug(2, "Processing directory " + bindir)
        directory = path + "/" + bindir
        process_dir (directory, d)

python relocatable_sysroot_preprocess() {
    rpath_replace(d.expand('${SYSROOT_DESTDIR}'), d)
}

python relocatable_package_preprocess() {
    if bb.data.inherits_class('nativesdk', d):
        rpath_replace(d.expand('${PKGD}'), d)
}

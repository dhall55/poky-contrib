# SDK packaging helper functions
#

def sdk_gen_pkgs(a, d):
	gen_pkgs = bb.data.getVar('PACKAGES_SDK_GEN', d, 1)
	if gen_pkgs == "1":
		return 'generate_sdk_pkgs'
	else:
		return ''

python generate_sdk_pkgs () {
    poky_pkgs = read_pkgdata('task-poky', d)['PACKAGES']
    pkgs = bb.data.getVar('PACKAGES', d, 1).split()
    for pkg in poky_pkgs.split():
        newpkg = pkg.replace('task-poky', 'task-poky-sdk')

        # for each of the task packages, add a corresponding sdk task
        pkgs.append(newpkg)

        # for each sdk task, take the rdepends of the non-sdk task, and turn
        # that into rrecommends upon the -dev versions of those, not unlike
        # the package depchain code
        spkgdata = read_subpkgdata(pkg, d)

        rdepends = explode_deps(spkgdata.get('RDEPENDS_%s' % pkg) or '')
        rreclist = []

        for depend in rdepends:
            split_depend = depend.split(' (')
            name = split_depend[0].strip()
            if packaged('%s-dev' % name, d):
                rreclist.append('%s-dev' % name)
            else:
                deppkgdata = read_subpkgdata(name, d)
                rdepends2 = explode_deps(deppkgdata.get('RDEPENDS_%s' % name) or '')
                for depend in rdepends2:
                    split_depend = depend.split(' (')
                    name = split_depend[0].strip()
                    if packaged('%s-dev' % name, d):
                        rreclist.append('%s-dev' % name)

            oldrrec = bb.data.getVar('RRECOMMENDS_%s' % newpkg, d) or ''
            bb.data.setVar('RRECOMMENDS_%s' % newpkg, oldrrec + ' ' + ' '.join(rreclist), d)
            # bb.note('RRECOMMENDS_%s = "%s"' % (newpkg, bb.data.getVar('RRECOMMENDS_%s' % newpkg, d)))

    # bb.note('pkgs is %s' % pkgs)
    bb.data.setVar('PACKAGES', ' '.join(pkgs), d)
}

#PACKAGES_DYNAMIC = "task-poky-sdk-*"

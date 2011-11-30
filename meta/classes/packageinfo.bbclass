inherit packagedata

python do_package_info () {
    bb.build.exec_func("read_subpackage_metadata", d)
    pn = d.getVar('PN', True) or ""
    pv = d.getVar('PV', True) or ""
    pr = d.getVar('PR', True) or ""
    recipe = pn + '-' + pv + '-' + pr

    packages = d.getVar('PACKAGES', True) or ""
    pkginfolist = []
    for pkg in packages.split():
        pkginfo = {}
        pkginfo['pkg'] = pkg
        pkginfo['pkgv'] = d.getVar('PKGV', True) or ""
        pkginfo['pkgr'] = d.getVar('PKGR', True) or ""
        pkginfo['pkg_rename'] = d.getVar('PKG_%s' % pkg, True) or ""
        pkginfo['section'] = d.getVar('SECTION', True) or ""
        pkginfo['summary'] = d.getVar('SUMMARY', True) or ""
        pkginfo['rdep'] = d.getVar('RDEPENDS_%s' % pkg, True) or ""
        pkginfo['rprov'] = d.getVar('RPROVIDES_%s' % pkg, True) or ""
        pkginfo['size'] = d.getVar('PKGSIZE_%s' % pkg, True) or ""
        pkginfo['allow_empty'] = d.getVar('ALLOW_EMTPY_%s' % pkg, True) or d.getVar('ALLOW_EMPTY', True) or ""
        pkginfolist.append(pkginfo)

    bb.event.fire(bb.event.PackageInfo(recipe, pkginfolist), d)
}
do_package_info[nostamp] = "1"
addtask package_info after do_package_write

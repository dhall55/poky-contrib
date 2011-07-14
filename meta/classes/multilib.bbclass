python multilib_virtclass_handler () {
    if not isinstance(e, bb.event.RecipePreFinalise):
        return

    cls = e.data.getVar("BBEXTENDCURR", True)
    variant = e.data.getVar("BBEXTENDVARIANT", True)
    if cls != "multilib" or not variant:
        return
 
    override = ":virtclass-multilib-" + variant

    bb.data.setVar("PN", variant + "-" + bb.data.getVar("PN", e.data, False), e.data)
    bb.data.setVar("SHLIBSDIR_virtclass-multilib-" + variant ,bb.data.getVar("SHLIBSDIR",e.data,False) + "/" + variant, e.data)
    bb.data.setVar("TARGET_VENDOR_virtclass-multilib-" + variant, "-pokyml" + variant, e.data)
    bb.data.setVar("OVERRIDES", bb.data.getVar("OVERRIDES", e.data, False) + override, e.data)
}

addhandler multilib_virtclass_handler

STAGINGCC_prepend = "${BBEXTENDVARIANT}-"

python __anonymous () {
    variant = d.getVar("BBEXTENDVARIANT", True)
    d.setVar("MLPREFIX", variant + "-")

    def extend_name(name):
        subs = name
        if name.startswith("virtual/"):
            subs = name.split("/", 1)[1]
            if not subs.startswith(variant):
                return "virtual/" + variant + "-" + subs
            return name
        if not subs.startswith(variant):
            return variant + "-" + subs
        return name


    def map_dependencies(varname, d, suffix = ""):
        if suffix:
            varname = varname + "_" + suffix
        deps = bb.data.getVar(varname, d, True)
        if not deps:
            return
        deps = bb.utils.explode_deps(deps)
        newdeps = []
        for dep in deps:
            if dep.endswith("-native"):
                newdeps.append(dep)
            else:
                newdeps.append(extend_name(dep))
        bb.data.setVar(varname, " ".join(newdeps), d)

    pkgs = []
    pkgrename = {}
    for pkg in (d.getVar("PACKAGES", True) or "").split():
        if pkg.startswith(variant):
            pkgs.append(pkg)
            continue
        pkgrename[pkg] = extend_name(pkg)
        pkgs.append(pkgrename[pkg])

    if pkgrename:
        d.setVar("PACKAGES", " ".join(pkgs))
        for pkg in pkgrename:
            for subs in ["FILES", "RDEPENDS", "RRECOMMENDS", "SUMMARY", "DESCRIPTION", "RSUGGESTS", "PROVIDES", "RCONFLICTS"]:
                d.renameVar("%s_%s" % (subs, pkg), "%s_%s" % (subs, pkgrename[pkg]))

    pn = d.getVar("PN", True)
    map_dependencies("DEPENDS", d)
    for pkg in (d.getVar("PACKAGES", True).split() + [""]):
        map_dependencies("RDEPENDS", d, pkg)
        map_dependencies("RRECOMMENDS", d, pkg)
        map_dependencies("RSUGGESTS", d, pkg)
        map_dependencies("RPROVIDES", d, pkg)
        map_dependencies("RREPLACES", d, pkg)

    newprovs = []
    provides = bb.data.getVar("PROVIDES", d, True)
    for prov in provides.split():
        newprovs.append(extend_name(prov))
    bb.data.setVar("PROVIDES", " ".join(newprovs), d)
}

class ClassExtender(object):
    def __init__(self, extname, d):
        self.extname = extname
        self.d = d
        self.pkgs_mapping = []

    def extend_name(self, name):
        if name.startswith("kernel-module"):
            return name
        if name.startswith("rtld"):
            return name
        if name.endswith("-" + self.extname):
            name = name.replace("-" + self.extname, "")
        if name.startswith("virtual/"):
            subs = name.split("/", 1)[1]
            if not subs.startswith(self.extname):
                return "virtual/" + self.extname + "-" + subs
            return name
        if not name.startswith(self.extname):
            return self.extname + "-" + name
        return name

    def map_variable(self, varname, setvar = True):
        var = self.d.getVar(varname, True)
        if not var:
            return ""
        var = var.split()
        newvar = []
        for v in var:
            newvar.append(self.extend_name(v))
        newdata =  " ".join(newvar)
        if setvar:
            self.d.setVar(varname, newdata)
        return newdata

    def map_regexp_variable(self, varname, setvar = True):
        var = self.d.getVar(varname, True)
        if not var:
            return ""
        var = var.split()
        newvar = []
        for v in var:
            if v.startswith("^"):
                newvar.append("^" + self.extname + "-" + v[1:])
            else:
                newvar.append(self.extend_name(v))
        newdata =  " ".join(newvar)
        if setvar:
            self.d.setVar(varname, newdata)
        return newdata

    def map_depends(self, dep):
        if dep.endswith(("-native", "-native-runtime")):
            return dep
        else:
            return self.extend_name(dep)

    def map_depends_variable(self, varname, suffix = ""):
        if suffix:
            varname = varname + "_" + suffix
        deps = self.d.getVar(varname, True)
        if not deps:
            return
        deps = bb.utils.explode_deps(deps)
        newdeps = []
        for dep in deps:
            newdeps.append(self.map_depends(dep))
        self.d.setVar(varname, " ".join(newdeps))

    def map_packagevars(self):
        for pkg in (self.d.getVar("PACKAGES", True).split() + [""]):
            self.map_depends_variable("RDEPENDS", pkg)
            self.map_depends_variable("RRECOMMENDS", pkg)
            self.map_depends_variable("RSUGGESTS", pkg)
            self.map_depends_variable("RPROVIDES", pkg)
            self.map_depends_variable("RREPLACES", pkg)
            self.map_depends_variable("RCONFLICTS", pkg)
            self.map_depends_variable("PKG", pkg)

    def rename_packages(self):
        for pkg in (self.d.getVar("PACKAGES", True) or "").split():
            if pkg.startswith(self.extname):
               self.pkgs_mapping.append([pkg.split(self.extname + "-")[1], pkg])
               continue
            self.pkgs_mapping.append([pkg, self.extend_name(pkg)])

        self.d.setVar("PACKAGES", " ".join([row[1] for row in self.pkgs_mapping]))

    def rename_package_variables(self, variables):
        for pkg_mapping in self.pkgs_mapping:
            for subs in variables:
                self.d.renameVar("%s_%s" % (subs, pkg_mapping[0]), "%s_%s" % (subs, pkg_mapping[1]))

class NativesdkClassExtender(ClassExtender):
    def map_depends(self, dep):
        if dep.endswith(("-native", "-native-runtime", "-cross")):
            return dep
        elif dep.endswith(("-gcc-intermediate", "-gcc-initial", "-gcc", "-g++")):
            return dep + "-crosssdk"
        else:
            return self.extend_name(dep)

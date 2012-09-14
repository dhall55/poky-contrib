# Populates LICENSE_DIRECTORY as set in distro config with the license files as set by
# LIC_FILES_CHKSUM.
# TODO:
# - There is a real issue revolving around license naming standards.
MANIFEST_DIRECTORY ??= "${DEPLOY_DIR}/license_manifests"
LICENSE_DIRECTORY ??= "${DEPLOY_DIR}/licenses"
LICSSTATEDIR = "${WORKDIR}/license-destdir/"

addtask populate_lic after do_patch before do_package
do_populate_lic[dirs] = "${LICSSTATEDIR}/${PN}"
do_populate_lic[cleandirs] = "${LICSSTATEDIR}"

# Standards are great! Everyone has their own. In an effort to standardize licensing
# names, common-licenses will use the SPDX standard license names. In order to not
# break the non-standardized license names that we find in LICENSE, we'll set
# up a bunch of VarFlags to accomodate non-SPDX license names.
#
# We should really discuss standardizing this field, but that's a longer term goal.
# For now, we can do this and it should grab the most common LICENSE naming variations.
#
# We should NEVER have a GPL/LGPL without a version!!!!
# Any mapping to MPL/LGPL/GPL should be fixed
# see: https://wiki.yoctoproject.org/wiki/License_Audit

# GPL variations
SPDXLICENSEMAP[GPL-1] = "GPL-1.0"
SPDXLICENSEMAP[GPLv1] = "GPL-1.0"
SPDXLICENSEMAP[GPLv1.0] = "GPL-1.0"
SPDXLICENSEMAP[GPL-2] = "GPL-2.0"
SPDXLICENSEMAP[GPLv2] = "GPL-2.0"
SPDXLICENSEMAP[GPLv2.0] = "GPL-2.0"
SPDXLICENSEMAP[GPL-3] = "GPL-3.0"
SPDXLICENSEMAP[GPLv3] = "GPL-3.0"
SPDXLICENSEMAP[GPLv3.0] = "GPL-3.0"

#LGPL variations
SPDXLICENSEMAP[LGPLv2] = "LGPL-2.0"
SPDXLICENSEMAP[LGPLv2.0] = "LGPL-2.0"
SPDXLICENSEMAP[LGPL2.1] = "LGPL-2.1"
SPDXLICENSEMAP[LGPLv2.1] = "LGPL-2.1"
SPDXLICENSEMAP[LGPLv3] = "LGPL-3.0"

#MPL variations
SPDXLICENSEMAP[MPL-1] = "MPL-1.0"
SPDXLICENSEMAP[MPLv1] = "MPL-1.0"
SPDXLICENSEMAP[MPLv1.1] = "MPL-1.1"
SPDXLICENSEMAP[MPLv2] = "MPL-2.0"

#MIT variations
SPDXLICENSEMAP[MIT-X] = "MIT"
SPDXLICENSEMAP[MIT-style] = "MIT"

#Openssl variations
SPDXLICENSEMAP[openssl] = "OpenSSL"

#Python variations
SPDXLICENSEMAP[PSF] = "Python-2.0"
SPDXLICENSEMAP[PSFv2] = "Python-2.0"
SPDXLICENSEMAP[Python-2] = "Python-2.0"

#Apache variations
SPDXLICENSEMAP[Apachev2] = "Apache-2.0"
SPDXLICENSEMAP[Apache-2] = "Apache-2.0"

#Artistic variations
SPDXLICENSEMAP[Artisticv1] = "Artistic-1.0"
SPDXLICENSEMAP[Artistic-1] = "Artistic-1.0"

#Academic variations
SPDXLICENSEMAP[AFL-2] = "AFL-2.0"
SPDXLICENSEMAP[AFL-1] = "AFL-1.2"
SPDXLICENSEMAP[AFLv2] = "AFL-2.0"
SPDXLICENSEMAP[AFLv1] = "AFL-1.2"

#Other variations
SPDXLICENSEMAP[EPLv1.0] = "EPL-1.0"
     
python license_create_pkg_manifest() {
    import bb.build
    import bb.event
    import bb.data
    import datetime
    import os
    now = datetime.datetime.now()
    if isinstance(e, bb.event.BuildStarted):
        #Set the main image name to somethine we know doesn't get changed
        e.data.setVar('MANIFEST_IMAGE_NAME', e.getPkgs()[0])
        image_name = e.data.getVar('MANIFEST_IMAGE_NAME', True)
        # All packages that get installed to the rootfs end up here.
        image_manifest_dir = os.path.join(e.data.getVar('MANIFEST_DIRECTORY', True), image_name)
        try:
            bb.mkdirhier(image_manifest_dir)
        except:
            pass
        spdx_license_manifest = os.path.join(image_manifest_dir, "license.rdf")
        license_manifest = os.path.join(image_manifest_dir, "license.manifest")
        try:
             os.remove(spdx_license_manifest)
        except:
             pass
        try:
             os.remove(license_manifest)
        except:
             pass
        # The rdf file isn't exactly SPDX complaint. We explain that in a link 
        # in <CreatorComment> to the wiki.
        if e.data.getVar('GENERATE_SPDX', True):
            fout = ""
            fout = "<rdf:RDF>\n"
            fout = fout + '<SpdxDocument rdf:about"http://www.spdx.org/tools#SPDXANALYSIS">\n'
            fout = fout + "<specVersion>Yocto-Lite-SPDX-1.0</specVersion>\n"
            fout = fout + '<dataLicense rdf:resource="http://spdx.org/licenses/PDDL-1.0" />\n'
            fout = fout + "<CreationInfo>\n"
            fout = fout + "<created>" + now.strftime("%Y-%m-%d %H:%M:%S") + "</created>\n"
            if e.data.getVar('LICENSE_CREATOR_ORG', True):
                fout = fout + "<creator>Organization: "+e.data.getVar('LICENSE_CREATOR_ORG', True) +"\n</creator>\n"
            if e.data.getVar('LICENSE_CREATOR_EMAIL', True):
                fout = fout + "<creator>Person:"+e.data.getVar('LICENSE_CREATOR_EMAIL', True) +"\n</creator>\n"
            fout = fout + "<creator>Tool: OpenEmbedded Core Build System Generated</creator>\n"
            fout = fout + "<CreatorComment>Manifest generated by OE-Core.</CreatorComment>\n"
            fout = fout + "<CreatorComment>Manifest does not implement entire SPDX spec.</CreatorComment>\n"
            fout = fout + "<CreatorComment>For more information on our implementation, please see:.</CreatorComment>\n"
            fout = fout + "<CreatorComment>http://wiki.yoctoproject.org/Yocto_and_SPDX</CreatorComment>\n"
            fout = fout + "<ImageName>Build: "+ image_name + "</ImageName>\n"
            fout = fout + "</CreationInfo>\n"
            fout = fout + '<Packages>\n'
            spdx_license_manifest_file = open(spdx_license_manifest, "a")
            spdx_license_manifest_file.write(fout + "\n")
            spdx_license_manifest_file.close()

        # We still want to maintain plain text manifests.
        fout = ""
        fout = fout + "Image: " + image_name + "\n"
        fout = fout + "Date: " + now.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        if e.data.getVar('LICENSE_CREATOR_ORG', True):
            fout = fout + "Organization: "+e.data.getVar('LICENSE_CREATOR_ORG', True) +"\n"
        if e.data.getVar('LICENSE_CREATOR_EMAIL', True):
            fout = fout + "Email: "+e.data.getVar('LICENSE_CREATOR_EMAIL', True) +"\n"
        license_manifest_file = open(license_manifest, "a")
        license_manifest_file.write(fout + "\n")
        license_manifest_file.close()
        
    if isinstance(e, bb.build.TaskStarted):
        # Everything we care about should hit do_package*
        if "do_package" in e.task:
            image_name = e.data.getVar('MANIFEST_IMAGE_NAME', True)
            pn = e.data.getVar('PN', True)
            if "-native" not in pn and "-cross" not in pn and "-intermediate" not in pn and "-initial" not in pn:
                image_manifest_dir = os.path.join(os.path.join(e.data.getVar('MANIFEST_DIRECTORY', True), image_name), pn)
                try:
                    bb.mkdirhier(image_manifest_dir)
                except:
                    pass
                spdx_license_manifest = os.path.join(image_manifest_dir, "license.rdf")
                license_manifest = os.path.join(image_manifest_dir, "license.manifest")
                # Yank the old manifests and try again. Important during sstate builds
                try:
                     os.remove(spdx_license_manifest)
                except:
                     pass
                try:
                     os.remove(license_manifest)
                except:
                     pass
                pv = e.data.getVar('PV', True)
                src_uri = e.data.getVar("SRC_URI", True).split()
                lic = e.data.getVar('LICENSE', True)
                pn_lic = e.data.getVar("LICENSE_" + pn, True)
                description = e.data.getVar("DESCRIPTION", True)
                homepage = e.data.getVar("HOMEPAGE", True)
                if e.data.getVar('GENERATE_SPDX', True):
                    fout = ""
                    fout = fout + '<Package rdf:about"http://www.spdx.org/tools#SPDXANALYSIS">\n<name>' + pn + ' ' + pv +'</name>\n'
                    fout = fout + "<description>" + description +"</description>\n"
                    fout = fout + '<packageFileName>' + pn + '<packageFileName>'
                    if e.data.getVar('LICENSE_CREATOR_EMAIL', True):
                        fout = fout + "<supplier>Person:"+e.data.getVar('LICENSE_CREATOR_EMAIL', True) +"</supplier>\n"
                    fout = fout + "<versionInfo>" + pv +"</versionInfo>\n"
                    if e.data.getVar('LICENSE_CREATOR_EMAIL', True):
                        fout = fout + "<originator>"+e.data.getVar('LICENSE_CREATOR_EMAIL', True) +"</originator>\n"
                    # downloadLocation is required for SPDX-1.0. If you are creating a package
                    # then this should be manually set. There could be some interesting work 
                    # around this, specifically around creation of package feeds during a bitbake
                    # run.
                    fout = fout + "<downloadLocation>UNKNOWN</downloadLocation>\n"
                    fout = fout + "<packageSupplier>" + homepage + "</packageSupplier>\n"
                    for url in src_uri:
                        fout = fout + "<sourceInfo>" + url + "</sourceInfo>\n"
                    fout = fout + "<LicenseDeclared>" 
                    if pn_lic:
                        licenses=pn_lic
                    else:
                        licenses=lic
                    fout = fout + '(' + licenses.replace('&', ' and ').replace('|', 'or') + ')'
                    fout = fout + "</LicenseDeclared>\n"
                    fout = fout + '</Package>'
                    spdx_license_manifest_file = open(spdx_license_manifest, "w")
                    spdx_license_manifest_file.write(fout + "\n")
                    spdx_license_manifest_file.close()

                # switch back to plain text manifests
                fout = ""
                fout = fout + "Package: " + pn + "\n"
                fout = fout + "Description: " + description + "\n"
                fout = fout + "Version: " + pv + "\n"
                fout = fout + "Homepage: " + homepage + "\n"
                if pn_lic:
                    fout = fout + "License: " + pn_lic + "\n"
                else: 
                    fout = fout + "License: " + lic + "\n"
                license_manifest_file = open(license_manifest, "w")
                license_manifest_file.write(fout + "\n")
                license_manifest_file.close()
}

python do_license_create_rootfs_manifest() {
    import os
    import shutil
    image_name = d.getVar('MANIFEST_IMAGE_NAME', True)
    manifest_dir = d.getVar('MANIFEST_DIRECTORY', True)
    # All packages that get installed to the rootfs end up here.
    image_manifest_dir = os.path.join(manifest_dir, image_name)
    try:
        bb.mkdirhier(image_manifest_dir)
    except:
        pass
    spdx_license_manifest = os.path.join(image_manifest_dir, "license.rdf")
    license_manifest = os.path.join(image_manifest_dir, "license.manifest")
    image_rootfs = d.getVar('IMAGE_ROOTFS', True)
    image_rfs_cl = os.path.join(image_rootfs, "/usr/share/common-licenses/")

    # list_installed_packages does just that. List things that are 
    # packaged up and installed on the image. 
    # Not everything on the image is actually installed via a package 
    # and I wanted to avoid utilizing list_installed_packages because I 
    # can see why we would not want things (like the bootloader) 
    # included in it's output, but I  do, however, need it for 
    # manifests. This code makes sure that everything that hit
    # do_package is included into the manifest.

    for dirs in os.listdir(image_manifest_dir):
        pkg_man_dir = os.path.join(image_manifest_dir, dirs)
        if os.path.isdir(pkg_man_dir):
            pkg_spdx_rdf = os.path.join(pkg_man_dir, "license.rdf")
            pkg_lic_man = os.path.join(pkg_man_dir, "license.manifest")
            pkg_lic_dir = os.path.join(d.getVar('LICENSE_DIRECTORY', True), dirs)
            rootfs_lic_dir = os.path.join(image_rfs_cl, dirs)
            if d.getVar('GENERATE_SPDX', True):
                pkg_spdx_rdf_file = open(pkg_spdx_rdf, "r")
                fout = pkg_spdx_rdf_file.read()
                spdx_license_manifest_file = open(spdx_license_manifest, "a")
                spdx_license_manifest_file.write(fout + "\n")
                spdx_license_manifest_file.close()
                pkg_spdx_rdf_file.close()
            pkg_lic_man_file = open(pkg_lic_man, "r")
            fout = pkg_lic_man_file.read()
            license_manifest_file = open(license_manifest, "a")
            license_manifest_file.write(fout + "\n")
            license_manifest_file.close()
            if d.getVar('COPY_LIC_DIRS', True):
                try:
                    bb.mkdirhier(rootfs_lic_dir)
                except:
                    pass
                for lic in os.listdir(pkg_lic_dir):
                    if os.path.isfile(os.path.join(pkg_lic_dir, lic)):
                        # Really don't need to copy the generics as they're 
                        # represented in the manifest and in the actual pkg licenses
                        # Doing so would make your image quite a bit larger
                        if "generic_" in lic: 
                            if not os.path.exists(os.path.join(image_rfs_cl, lic)):
                                shutil.copyfile(os.path.join(pkg_lic_dir, lic), os.path.join(image_rfs_cl, lic))
                            os.symlink(os.path.join(image_rfs_cl, lic), os.path.join(rootfs_lic_dir, lic))
                        else:
                            shutil.copyfile(os.path.join(pkg_lic_dir, lic), os.path.join(rootfs_lic_dir, lic))

    if d.getVar('GENERATE_SPDX', True):
        fout = ""
        fout = "</Packages>"
        fout = fout + "</SpdxDocument>\n</rdf:RDF>"
        spdx_license_manifest_file = open(spdx_license_manifest, "a")
        spdx_license_manifest_file.write(fout + "\n")
        spdx_license_manifest_file.close()
    if d.getVar('COPY_LIC_MANIFEST', True):
        try:
            bb.mkdirhier(image_rfs_cl)
        except:
            pass
        shutil.copyfile(license_manifest, os.path.join(image_rfs_cl, license.manifest))
        if d.getVar('GENERATE_SPDX', True):
            shutil.copyfile(spdx_license_manifest, os.path.join(image_rfs_cl, license.rdf))
}

python do_populate_lic() {
    """
    Populate LICENSE_DIRECTORY with licenses.
    """
    import shutil
    import oe.license

    pn = d.getVar('PN', True)
    for package in d.getVar('PACKAGES', True):
        if d.getVar('LICENSE_' + pn + '-' + package, True):
            license_types = license_types + ' & ' + \
                            d.getVar('LICENSE_' + pn + '-' + package, True)

    #If we get here with no license types, then that means we have a recipe 
    #level license. If so, we grab only those.
    try:
        license_types
    except NameError:        
        # All the license types at the recipe level
        license_types = d.getVar('LICENSE', True)
 
    # All the license files for the package
    lic_files = d.getVar('LIC_FILES_CHKSUM', True)
    pn = d.getVar('PN', True)
    # The base directory we wrangle licenses to
    destdir = os.path.join(d.getVar('LICSSTATEDIR', True), pn)
    # The license files are located in S/LIC_FILE_CHECKSUM.
    srcdir = d.getVar('S', True)
    # Directory we store the generic licenses as set in the distro configuration
    generic_directory = d.getVar('COMMON_LICENSE_DIR', True)
    license_source_dirs = []
    license_source_dirs.append(generic_directory)
    try:
        additional_lic_dirs = d.getVar('LICENSE_PATH', True).split()
        for lic_dir in additional_lic_dirs:
            license_source_dirs.append(lic_dir)
    except:
        pass

    class FindVisitor(oe.license.LicenseVisitor):
        def visit_Str(self, node):
            #
            # Until I figure out what to do with
            # the two modifiers I support (or greater = +
            # and "with exceptions" being *
            # we'll just strip out the modifier and put
            # the base license.
            find_license(node.s.replace("+", "").replace("*", ""))
            self.generic_visit(node)

    def find_license(license_type):
        try:
            bb.mkdirhier(gen_lic_dest)
        except:
            pass
        spdx_generic = None
        license_source = None
        # If the generic does not exist we need to check to see if there is an SPDX mapping to it
        for lic_dir in license_source_dirs:
            if not os.path.isfile(os.path.join(lic_dir, license_type)):
                if d.getVarFlag('SPDXLICENSEMAP', license_type) != None:
                    # Great, there is an SPDXLICENSEMAP. We can copy!
                    bb.debug(1, "We need to use a SPDXLICENSEMAP for %s" % (license_type))
                    spdx_generic = d.getVarFlag('SPDXLICENSEMAP', license_type)
                    license_source = lic_dir
                    break
            elif os.path.isfile(os.path.join(lic_dir, license_type)):
                spdx_generic = license_type
                license_source = lic_dir
                break

        if spdx_generic and license_source:
            # we really should copy to generic_ + spdx_generic, however, that ends up messing the manifest
            # audit up. This should be fixed in emit_pkgdata (or, we actually got and fix all the recipes)

            bb.copyfile(os.path.join(license_source, spdx_generic), os.path.join(os.path.join(d.getVar('LICSSTATEDIR', True), pn), "generic_" + license_type))
            if not os.path.isfile(os.path.join(os.path.join(d.getVar('LICSSTATEDIR', True), pn), "generic_" + license_type)):
            # If the copy didn't occur, something horrible went wrong and we fail out
                bb.warn("%s for %s could not be copied for some reason. It may not exist. WARN for now." % (spdx_generic, pn))
        else:
            # And here is where we warn people that their licenses are lousy
            bb.warn("%s: No generic license file exists for: %s in any provider" % (pn, license_type))
            pass

    try:
        bb.mkdirhier(destdir)
    except:
        pass

    if not generic_directory:
        raise bb.build.FuncFailed("COMMON_LICENSE_DIR is unset. Please set this in your distro config")

    if not lic_files:
        # No recipe should have an invalid license file. This is checked else
        # where, but let's be pedantic
        bb.note(pn + ": Recipe file does not have license file information.")
        return True

    for url in lic_files.split():
        (type, host, path, user, pswd, parm) = bb.decodeurl(url)
        # We want the license file to be copied into the destination
        srclicfile = os.path.join(srcdir, path)
        ret = bb.copyfile(srclicfile, os.path.join(destdir, os.path.basename(path)))
        # If the copy didn't occur, something horrible went wrong and we fail out
        if not ret:
            bb.warn("%s could not be copied for some reason. It may not exist. WARN for now." % srclicfile)

    v = FindVisitor()
    try:
        v.visit_string(license_types)
    except oe.license.InvalidLicense as exc:
        bb.fatal('%s: %s' % (d.getVar('PF', True), exc))
    except SyntaxError:
        bb.warn("%s: Failed to parse it's LICENSE field." % (d.getVar('PF', True)))

}

def return_spdx(d, license):
    """
    This function returns the spdx mapping of a license.
    """
    if d.getVarFlag('SPDXLICENSEMAP', license) != None:
        return license
    else:
        return d.getVarFlag('SPDXLICENSEMAP', license_type)

def incompatible_license(d, dont_want_license, package=""):
    """
    This function checks if a recipe has only incompatible licenses. It also take into consideration 'or'
    operand.
    """
    import re
    import oe.license
    from fnmatch import fnmatchcase as fnmatch
    pn = d.getVar('PN', True)
    dont_want_licenses = []
    dont_want_licenses.append(d.getVar('INCOMPATIBLE_LICENSE', True))
    recipe_license = d.getVar('LICENSE', True)
    if package != "":
        if d.getVar('LICENSE_' + pn + '-' + package, True):
            license = d.getVar('LICENSE_' + pn + '-' + package, True)
        else:
            license = recipe_license
    else:
        license = recipe_license
    spdx_license = return_spdx(d, dont_want_license)
    dont_want_licenses.append(spdx_license)

    def include_license(license):
        if any(fnmatch(license, pattern) for pattern in dont_want_licenses):
            return False
        else:
            return True

    def choose_licenses(a, b):
        if all(include_license(lic) for lic in a):
            return a
        else:
            return b

    """
    If you want to exlude license named generically 'X', we surely want to exlude 'X+' as well.
    In consequence, we will exclude the '+' character from LICENSE in case INCOMPATIBLE_LICENSE
    is not a 'X+' license.
    """
    if not re.search(r'[+]',dont_want_license):
        licenses=oe.license.flattened_licenses(re.sub(r'[+]', '', license), choose_licenses)
    else:
        licenses=oe.license.flattened_licenses(license, choose_licenses)

    for onelicense in licenses:
        if not include_license(onelicense):
            return True
    return False

def check_license_flags(d):
    """
    This function checks if a recipe has any LICENSE_FLAGs that
    aren't whitelisted.

    If it does, it returns the first LICENSE_FLAG missing from the
    whitelist, or all the LICENSE_FLAGs if there is no whitelist.

    If everything is is properly whitelisted, it returns None.
    """

    def license_flag_matches(flag, whitelist, pn):
        """
        Return True if flag matches something in whitelist, None if not.

        Before we test a flag against the whitelist, we append _${PN}
        to it.  We then try to match that string against the
        whitelist.  This covers the normal case, where we expect
        LICENSE_FLAGS to be a simple string like 'commercial', which
        the user typically matches exactly in the whitelist by
        explicitly appending the package name e.g 'commercial_foo'.
        If we fail the match however, we then split the flag across
        '_' and append each fragment and test until we either match or
        run out of fragments.
        """
        flag_pn = ("%s_%s" % (flag, pn))
        for candidate in whitelist:
            if flag_pn == candidate:
                    return True

        flag_cur = ""
        flagments = flag_pn.split("_")
        flagments.pop() # we've already tested the full string
        for flagment in flagments:
            if flag_cur:
                flag_cur += "_"
            flag_cur += flagment
            for candidate in whitelist:
                if flag_cur == candidate:
                    return True
        return False

    def all_license_flags_match(license_flags, whitelist):
        """ Return first unmatched flag, None if all flags match """
        pn = d.getVar('PN', True)
        split_whitelist = whitelist.split()
        for flag in license_flags.split():
            if not license_flag_matches(flag, split_whitelist, pn):
                return flag
        return None

    license_flags = d.getVar('LICENSE_FLAGS', True)
    if license_flags:
        whitelist = d.getVar('LICENSE_FLAGS_WHITELIST', True)
        if not whitelist:
            return license_flags
        unmatched_flag = all_license_flags_match(license_flags, whitelist)
        if unmatched_flag:
            return unmatched_flag
    return None

SSTATETASKS += "do_populate_lic"
do_populate_lic[sstate-name] = "populate-lic"
do_populate_lic[sstate-inputdirs] = "${LICSSTATEDIR}"
do_populate_lic[sstate-outputdirs] = "${LICENSE_DIRECTORY}/"

python do_populate_lic_setscene () {
    sstate_setscene(d)
}

addtask do_populate_lic_setscene

addtask do_license_create_rootfs_manifest before do_rootfs

addhandler license_create_pkg_manifest

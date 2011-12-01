#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao xu <dongxiao.xu@intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import gtk
import gobject
import re

class PackageListModel(gtk.TreeStore):
    """
    This class defines an gtk.TreeStore subclass which will convert the output
    of the bb.event.TargetsTreeGenerated event into a gtk.TreeStore whilst also
    providing convenience functions to access gtk.TreeModel subclasses which
    provide filtered views of the data.
    """
    (COL_PKGNAME, COL_VER, COL_REV, COL_RNM, COL_SEC, COL_SUM, COL_RDEP, COL_RPROV, COL_SIZE, COL_BINB, COL_INC) = range(11)

    __gsignals__ = {
        "packagelist-populated" : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        "contents-changed"   : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                (gobject.TYPE_INT,)),
        "image-changed"      : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                (gobject.TYPE_STRING,)),
        }

    """
    """
    def __init__(self):
        self.contents = None
        self.packages = None
        self.images = None
        self.selected_image = None
        
        gtk.TreeStore.__init__ (self,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN)

    """
    Helper function to determine whether an item is a package
    """
    def package_model_filter(self, model, it):
        name = model.get_value(it, self.COL_PKGNAME)
        return True

    """
    Create, if required, and return a filtered gtk.TreeModel
    """
    def packages_model(self):
        if not self.packages:
            self.packages = self.filter_new()
            self.packages.set_visible_func(self.package_model_filter)
        return self.packages

    def populate_recipe(self, recipe):
        pniter = self.append(None)
        self.set(pniter, self.COL_PKGNAME, recipe,
                         self.COL_INC, False)
        return pniter

    """
    The populate() function takes as input the data from a
    bb.event.TargetsTreeGenerated event and populates the TaskList.
    Once the population is done it emits gsignal packagelist-populated
    to notify any listeners that the model is ready
    """
    def populate(self, pniter, pkginfo):
        pkg = pkginfo['pkg']
        pkgv = pkginfo['pkgv']
        pkgr = pkginfo['pkgr']
        pkg_rename = pkginfo['pkg_rename']
        section = pkginfo['section']
        summary = pkginfo['summary']
        rdep = pkginfo['rdep']
        rprov = pkginfo['rprov']
        if len(pkginfo['size']) > 6:
            size = '%.1f' % (int(pkginfo['size'])*1.0/1024/1024) + ' MB'
        elif len(pkginfo['size']) > 3:
            size = '%.1f' % (int(pkginfo['size'])*1.0/1024) + ' KB'
        else:
            size = pkginfo['size'] + ' B'
        allow_empty = pkginfo['allow_empty']

        if size == "0" and not allow_empty:
            return

        self.set(self.append(pniter), self.COL_PKGNAME, pkg, self.COL_VER, pkgv,
                 self.COL_REV, pkgr, self.COL_RNM, pkg_rename,
                 self.COL_SEC, section, self.COL_SUM, summary,
                 self.COL_RDEP, rdep, self.COL_RPROV, rprov,
                 self.COL_SIZE, size, self.COL_BINB, "", self.COL_INC, False)

    """
    Check whether the item at item_path is included or not
    """
    def contents_includes_path(self, item_path):
        return self[item_path][self.COL_INC]

    """
    Mark a certain package as selected.
    All its dependencies are marked as selected.
    The recipe provides the package is marked as selected.
    If user explicitly selects a recipe, all its providing packages are selected
    """
    def include_item(self, item_path, binb="", image_contents=False):
        item_name = self[item_path][self.COL_PKGNAME]
        item_rdep = self[item_path][self.COL_RDEP]

        self[item_path][self.COL_INC] = True
        it = self.get_iter(item_path)

        # If user explicitly selects a recipe, all its providing packages are selected.
        if not self[item_path][self.COL_VER] and binb == "User Selected":
            child_it = self.iter_children(it)
            while child_it:
                child_path = self.get_path(child_it)
                child_included = self[child_path][self.COL_INC]
                if not child_included:
                    self.include_item(child_path, binb="User Selected", image_contents=False)
                child_it = self.iter_next(child_it)
            return

        # The recipe provides the package is also marked as selected
        parent_it = self.iter_parent(it)
        if parent_it:
            parent_path = self.get_path(parent_it)
            self[parent_path][self.COL_INC] = True

        item_bin = self[item_path][self.COL_BINB].split(', ')
        if binb and not binb in item_bin:
            item_bin.append(binb)
            self[item_path][self.COL_BINB] = ', '.join(item_bin).lstrip(', ')

        if item_rdep:
            # Ensure all of the items deps are included and, where appropriate,
            # add this item to their COL_BINB
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                # If the contents model doesn't already contain dep, add it
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_included = self.contents_includes_path(dep_path)

                if dep_included and not dep in item_bin:
                    # don't set the COL_BINB to this item if the target is an
                    # item in our own COL_BINB
                    dep_bin = self[dep_path][self.COL_BINB].split(', ')
                    if not item_name in dep_bin:
                        dep_bin.append(item_name)
                        self[dep_path][self.COL_BINB] = ', '.join(dep_bin).lstrip(', ')
                elif not dep_included:
                    self.include_item(dep_path, binb=item_name, image_contents=False)

    """
    Mark a certain package as de-selected.
    All other packages that depends on this package are marked as de-selected.
    If none of the packages provided by the recipe, the recipe should be marked as de-selected.
    If user explicitly de-select a recipe, all its providing packages are de-selected.
    """
    def exclude_item(self, item_path):
        self[item_path][self.COL_INC] = False
        item_name = self[item_path][self.COL_PKGNAME]
        item_rdep = self[item_path][self.COL_RDEP]
        it = self.get_iter(item_path)

        # If user explicitly de-select a recipe, all its providing packages are de-selected.
        if not self[item_path][self.COL_VER]:
            child_it = self.iter_children(it)
            while child_it:
                child_path = self.get_path(child_it)
                child_included = self[child_path][self.COL_INC]
                if child_included:
                    self.exclude_item(child_path)
                child_it = self.iter_next(child_it)
            return

        # If none of the packages provided by the recipe, the recipe should be marked as de-selected.
        parent_it = self.iter_parent(it)
        peer_iter = self.iter_children(parent_it)
        enabled = 0
        while peer_iter:
            peer_path = self.get_path(peer_iter)
            if self[peer_path][self.COL_INC]:
                enabled = 1
                break
            peer_iter = self.iter_next(peer_iter)
        if not enabled:
            parent_path = self.get_path(parent_it)
            self[parent_path][self.COL_INC] = False

        # All packages that depends on this package are de-selected.
        if item_rdep:
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_bin = self[dep_path][self.COL_BINB].split(', ')
                if item_name in dep_bin:
                    dep_bin.remove(item_name)
                    self[dep_path][self.COL_BINB] = ', '.join(dep_bin).lstrip(', ')

        item_bin = self[item_path][self.COL_BINB].split(', ')
        if item_bin:
            for binb in item_bin:
                binb_path = self.find_path_for_item(binb)
                if not binb_path:
                    continue
                self.exclude_item(binb_path)

    """
    Find the model path for the item_name
    Returns the path in the model or None
    """
    def find_path_for_item(self, item_name):

        it = self.get_iter_first()
        while it:
            child_it = self.iter_children(it)
            while child_it:
                if (self.get_value(child_it, self.COL_PKGNAME) == item_name):
                    return self.get_path(child_it)
                else:
                    child_it = self.iter_next(child_it)
            it = self.iter_next(it)
        return None

    def set_selected_packages(self, packagelist):
        selected = packagelist
        it = self.get_iter_first()

        while it:
            child_it = self.iter_children(it)
            while child_it:
                name = self.get_value(child_it, self.COL_PKGNAME)
                if name in packagelist:
                    packagelist.remove(name)
                    path = self.get_path(child_it)
                    self.include_item(item_path=path,
                                      binb="User Selected")
                    if len(packagelist) == 0:
                        return
                child_it = self.iter_next(child_it)
            it = self.iter_next(it)

    def get_selected_packages(self):
        it = self.get_iter_first()
        packagelist = []

        while it:
            child_it = self.iter_children(it)
            while child_it:
                if self.get_value(child_it, self.COL_INC):
                    name = self.get_value(child_it, self.COL_PKGNAME)
                    packagelist.append(name)
                child_it = self.iter_next(child_it)
            it = self.iter_next(it)

        return packagelist

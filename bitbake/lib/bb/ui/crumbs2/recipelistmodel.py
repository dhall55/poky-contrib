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

class RecipeListModel(gtk.ListStore):
    """
    This class defines an gtk.ListStore subclass which will convert the output
    of the bb.event.TargetsTreeGenerated event into a gtk.ListStore whilst also
    providing convenience functions to access gtk.TreeModel subclasses which
    provide filtered views of the data.
    """
    (COL_NAME, COL_DESC, COL_LIC, COL_GROUP, COL_DEPS, COL_BINB, COL_TYPE, COL_INC, COL_IMG, COL_PATH, COL_PN) = range(11)

    __gsignals__ = {
        "recipelist-populated" : (gobject.SIGNAL_RUN_LAST,
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
        self.tasks = None
        self.recipes = None
        self.images = None
        self.selected_image = None
        
        gtk.ListStore.__init__ (self,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN,
                                gobject.TYPE_BOOLEAN,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING)

    """
    Helper method to determine whether name is a target pn
    """
    def non_target_name(self, name):
        if ('-native' in name):
            return True
        return False

    def contents_changed_cb(self, tree_model, path, it=None):
        recipe_cnt = self.contents.iter_n_children(None)
        self.emit("contents-changed", recipe_cnt)

    def contents_model_filter(self, model, it):
        if not model.get_value(it, self.COL_INC) or model.get_value(it, self.COL_TYPE) == 'image':
            return False
        name = model.get_value(it, self.COL_NAME)
        if self.non_target_name(name):
            return False
        else:
            return True

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are to be included in the
    image
    """
    def contents_model(self):
        if not self.contents:
            self.contents = self.filter_new()
            self.contents.set_visible_func(self.contents_model_filter)
            self.contents.connect("row-inserted", self.contents_changed_cb)
            self.contents.connect("row-deleted", self.contents_changed_cb)
        return self.contents
    
    """
    Helper function to determine whether an item is a task
    """
    def task_model_filter(self, model, it):
        if model.get_value(it, self.COL_TYPE) == 'task':
            return True
        else:
            return False

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are tasks
    """
    def tasks_model(self):
        if not self.tasks:
            self.tasks = self.filter_new()
            self.tasks.set_visible_func(self.task_model_filter)
        return self.tasks

    """
    Helper function to determine whether an item is an image
    """
    def image_model_filter(self, model, it):
        if model.get_value(it, self.COL_TYPE) == 'image':
            return True
        else:
            return False

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are images
    """
    def images_model(self):
        if not self.images:
            self.images = self.filter_new()
            self.images.set_visible_func(self.image_model_filter)
        return self.images

    """
    Helper function to determine whether an item is a recipe
    """
    def recipe_model_filter(self, model, it):
        if model.get_value(it, self.COL_TYPE) != 'recipe':
            return False
        else:
            name = model.get_value(it, self.COL_NAME)
            if self.non_target_name(name):
                return False
            return True

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are recipes
    """
    def recipes_model(self):
        if not self.recipes:
            self.recipes = self.filter_new()
            self.recipes.set_visible_func(self.recipe_model_filter)
        return self.recipes

    def map_rdepends(self, event_model, rdep_type, name):
        if rdep_type not in ['pkg', 'pn']:
            return
        package_depends = event_model["rdepends-%s" % rdep_type].get(name, [])
        pn_depends = []
        for package_depend in package_depends:
            if 'task-' not in package_depend and package_depend in event_model["packages"].keys():
                pn_depends.append(event_model["packages"][package_depend]["pn"])
            else:
                pn_depends.append(package_depend)
        return list(set(pn_depends))

    def subpkg_populate(self, event_model, pkg, summary, lic, group, atype, filename, pn):
        pn_depends = " ".join(self.map_rdepends(event_model, "pkg", pkg))
        self.set(self.append(), self.COL_NAME, pkg, self.COL_DESC, summary,
                 self.COL_LIC, lic, self.COL_GROUP, group,
                 self.COL_DEPS, pn_depends, self.COL_BINB, "",
                 self.COL_TYPE, atype, self.COL_INC, False,
                 self.COL_IMG, False, self.COL_PATH, filename,
                 self.COL_PN, pn)

    """
    The populate() function takes as input the data from a
    bb.event.TargetsTreeGenerated event and populates the RecipeList.
    Once the population is done it emits gsignal recipelist-populated
    to notify any listeners that the model is ready
    """
    def populate(self, event_model):
        # First clear the model, in case repopulating
        self.clear()
        for item in event_model["pn"]:
            atype = 'recipe'
            name = item
            summary = event_model["pn"][item]["summary"]
            lic = event_model["pn"][item]["license"]
            group = event_model["pn"][item]["section"]
            filename = event_model["pn"][item]["filename"]

            if ('task-' in name):
                atype = 'task'
                for pkg in event_model["pn"][name]["packages"]:
                    self.subpkg_populate(event_model, pkg, summary, lic, group, atype, filename, name)
                continue

            elif ('-image-' in name):
                atype = 'image'
                rdepends = self.map_rdepends(event_model, "pn", name)
                depends = depends + rdepends

            else:
                depends = event_model["depends"].get(item, []) + self.map_rdepends(event_model, 'pn', item)
                for pkg in event_model["pn"][name]["packages"]:
                    depends += self.map_rdepends(event_model, 'pkg', item)

            self.set(self.append(), self.COL_NAME, item, self.COL_DESC, summary,
                     self.COL_LIC, lic, self.COL_GROUP, group,
                     self.COL_DEPS, " ".join(depends), self.COL_BINB, "",
                     self.COL_TYPE, atype, self.COL_INC, False,
                     self.COL_IMG, False, self.COL_PATH, filename,
                     self.COL_PN, item)

        self.emit("recipelist-populated")

    """
    Check whether the item at item_path is included or not
    """
    def contents_includes_path(self, item_path):
        return self[item_path][self.COL_INC]

    """
    Add this item, and any of its dependencies, to the image contents
    """
    def include_item(self, item_path, binb="", image_contents=False):
        item_name = self[item_path][self.COL_NAME]
        item_deps = self[item_path][self.COL_DEPS]

        self[item_path][self.COL_INC] = True

        item_bin = self[item_path][self.COL_BINB].split(', ')
        if binb and not binb in item_bin:
            item_bin.append(binb)
            self[item_path][self.COL_BINB] = ', '.join(item_bin).lstrip(', ')

        # We want to do some magic with things which are brought in by the
        # base image so tag them as so
        if image_contents:
            self[item_path][self.COL_IMG] = True
            if self[item_path][self.COL_TYPE] == 'image':
                self.selected_image = item_name

        if item_deps:
            # Ensure all of the items deps are included and, where appropriate,
            # add this item to their COL_BINB
            for dep in item_deps.split(" "):
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
                    self.include_item(dep_path, binb=item_name, image_contents=image_contents)

    def exclude_item(self, item_path):
        self[item_path][self.COL_INC] = False
        item_name = self[item_path][self.COL_NAME]
        item_deps = self[item_path][self.COL_DEPS]
        if item_deps:
            for dep in item_deps.split(" "):
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

    def format_cell(self, column, cell, model, iter, userdata=None):
        item_name = model.get_value(iter, self.COL_NAME)
        item_bin = model.get_value(iter, self.COL_BINB)
        item_inc = model.get_value(iter, self.COL_INC)
        if item_inc and not item_bin:
            cell.set_property("cell-background", "#ff0000")
        else:
            cell.set_property("cell-background", "#ffffff")

    """
    Find the model path for the item_name
    Returns the path in the model or None
    """
    def find_path_for_item(self, item_name):
        # We don't include virtual/* or *-native items in the model so save a
        # heavy iteration loop by exiting early for these items
        if self.non_target_name(item_name):
            return None

        it = self.get_iter_first()
        while it:
            if (self.get_value(it, self.COL_NAME) == item_name):
                return self.get_path(it)
            else:
                it = self.iter_next(it)
        return None

    """
    Empty self.contents by setting the include of each entry to None
    """
    def reset(self):
        # Deselect images - slightly more complex logic so that we don't
        # have to iterate all of the contents of the main model, instead
        # just iterate the images model.
        if self.selected_image:
            iit = self.images.get_iter_first()
            while iit:
                pit = self.images.convert_iter_to_child_iter(iit)
                self.set(pit, self.COL_INC, False)
                iit = self.images.iter_next(iit)
            self.selected_image = None

        it = self.contents.get_iter_first()
        while it:
            oit = self.contents.convert_iter_to_child_iter(it)
            self.set(oit,
                     self.COL_INC, False,
                     self.COL_BINB, "",
                     self.COL_IMG, False)
            # As we've just removed the first item...
            it = self.contents.get_iter_first()

    """
    Returns two lists. One of user selected recipes and the other containing
    all selected recipes
    """
    def get_selected_recipes(self):
        allrecipes = []
        userrecipes = []

        it = self.contents.get_iter_first()
        while it:
            sel = "User Selected" in self.contents.get_value(it, self.COL_BINB)
            name = self.contents.get_value(it, self.COL_PN)
            allrecipes.append(name)
            if sel:
                userrecipes.append(name)
            it = self.contents.iter_next(it)
        return list(set(userrecipes)), list(set(allrecipes))

    def set_selected_image(self, img):
        self.selected_image = img
        path = self.find_path_for_item(img)
        self.include_item(item_path=path,
                          binb="User Selected",
                          image_contents=True)

        self.emit("image-changed", self.selected_image)

    def set_selected_recipes(self, recipelist):
        selected = recipelist
        it = self.get_iter_first()

        while it:
            name = self.get_value(it, self.COL_NAME)
            if name in recipelist:
                recipelist.remove(name)
                path = self.get_path(it)
                self.include_item(item_path=path,
                                  binb="User Selected")
                if len(recipelist) == 0:
                    return
            it = self.iter_next(it)

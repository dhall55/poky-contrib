#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao Xu <dongxiao.xu@intel.com>
# Authored by Shane Wang <shane.wang@intel.com>
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
import pango
from bb.ui.crumbs.hobwidget import HobWidget

class RecipeListModel(gtk.ListStore):
    """
    This class defines an gtk.ListStore subclass which will convert the output
    of the bb.event.TargetsTreeGenerated event into a gtk.ListStore whilst also
    providing convenience functions to access gtk.TreeModel subclasses which
    provide filtered views of the data.
    """
    (COL_NAME, COL_DESC, COL_LIC, COL_GROUP, COL_DEPS, COL_BINB, COL_TYPE, COL_INC, COL_IMG, COL_INSTALL) = range(10)

    __gsignals__ = {
        "recipelist-populated" : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        "selected-recipes-changed" : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        }

    """
    """
    def __init__(self):
        self.tasks = None
        self.mltasks = None
        self.recipes = None
        self.mlrecipes = None
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
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING)

    """
    Helper method to determine whether name is a target pn
    """
    def non_target_name(self, name):
        if ('-native' in name):
            return True
        return False

    """
    Helper function to determine whether an item is a task
    """
    def mltask_model_filter(self, model, it):
        if model.get_value(it, self.COL_TYPE) == 'mltask':
            return True
        else:
            return False

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are tasks
    """
    def mltasks_model(self):
        if not self.mltasks:
            self.mltasks = self.filter_new()
            self.mltasks.set_visible_func(self.mltask_model_filter)
        return self.mltasks
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
    Helper function to determine whether an item is an image
    """
    def mlrecipe_model_filter(self, model, it):
        if model.get_value(it, self.COL_TYPE) == 'mlrecipe':
            return True
        else:
            return False

    """
    Create, if required, and return a filtered gtk.TreeModel
    containing only the items which are images
    """
    def mlrecipes_model(self):
        if not self.mlrecipes:
            self.mlrecipes = self.filter_new()
            self.mlrecipes.set_visible_func(self.mlrecipe_model_filter)
        return self.mlrecipes

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

    def map_runtime(self, event_model, runtime, rdep_type, name):
        if rdep_type not in ['pkg', 'pn'] or runtime not in ['rdepends', 'rrecs']:
            return
        package_depends = event_model["%s-%s" % (runtime, rdep_type)].get(name, [])
        pn_depends = []
        for package_depend in package_depends:
            if 'task-' not in package_depend and package_depend in event_model["packages"].keys():
                pn_depends.append(event_model["packages"][package_depend]["pn"])
            else:
                pn_depends.append(package_depend)
        return list(set(pn_depends))

    def subpkg_populate(self, event_model, pkg, summary, lic, group, atype, pn):
        pn_depends = self.map_runtime(event_model, "rdepends", "pkg", pkg)
        pn_depends += self.map_runtime(event_model, "rrecs", "pkg", pkg)
        self.set(self.append(), self.COL_NAME, pkg, self.COL_DESC, summary,
                 self.COL_LIC, lic, self.COL_GROUP, group,
                 self.COL_DEPS, " ".join(pn_depends), self.COL_BINB, "",
                 self.COL_TYPE, atype, self.COL_INC, False,
                 self.COL_IMG, False, self.COL_INSTALL, "")

    """
    The populate() function takes as input the data from a
    bb.event.TargetsTreeGenerated event and populates the RecipeList.
    Once the population is done it emits gsignal recipelist-populated
    to notify any listeners that the model is ready
    """
    def populate(self, event_model):
        # First clear the model, in case repopulating
        self.clear()

        # dummy image for prompt
        self.set(self.append(), self.COL_NAME, RecipeSelection.__dummy_image__,
                 self.COL_DESC, "Dummy image for prompt",
                 self.COL_LIC, "", self.COL_GROUP, "",
                 self.COL_DEPS, "", self.COL_BINB, "",
                 self.COL_TYPE, "image", self.COL_INC, False,
                 self.COL_IMG, False, self.COL_INSTALL, "")

        for item in event_model["pn"]:
            name = item
            summary = event_model["pn"][item]["summary"]
            lic = event_model["pn"][item]["license"]
            group = event_model["pn"][item]["section"]
            install = []

            if ('task-' in name):
                if ('lib32-' in name or 'lib64-' in name):
                    atype = 'mltask'
                else:
                    atype = 'task'
                for pkg in event_model["pn"][name]["packages"]:
                    self.subpkg_populate(event_model, pkg, summary, lic, group, atype, name)
                continue

            elif ('-image-' in name):
                atype = 'image'
                depends = event_model["depends"].get(item, [])
                rdepends = self.map_runtime(event_model, 'rdepends', 'pn', name)
                depends = depends + rdepends
                install = event_model["rdepends-pn"].get(item, [])

            elif ('meta-' in name):
                atype = 'toolchain'

            else:
                if ('lib32-' in name or 'lib64-' in name):
                    atype = 'mlrecipe'
                else:
                    atype = 'recipe'
                depends = event_model["depends"].get(item, [])
                depends += self.map_runtime(event_model, 'rdepends', 'pn', item)
                for pkg in event_model["pn"][name]["packages"]:
                    depends += self.map_runtime(event_model, 'rdepends', 'pkg', item)
                    depends += self.map_runtime(event_model, 'rrecs', 'pkg', item)

            self.set(self.append(), self.COL_NAME, item, self.COL_DESC, summary,
                     self.COL_LIC, lic, self.COL_GROUP, group,
                     self.COL_DEPS, " ".join(depends), self.COL_BINB, "",
                     self.COL_TYPE, atype, self.COL_INC, False,
                     self.COL_IMG, False, self.COL_INSTALL, " ".join(install))

        self.pn_path = {}
        it = self.get_iter_first()
        while it:
            pn = self.get_value(it, self.COL_NAME)
            path = self.get_path(it)
            self.pn_path[pn] = path
            it = self.iter_next(it)

        self.emit("recipelist-populated")

    """
    Add this item, and any of its dependencies, to the image contents
    """
    def include_item(self, item_path, binb="", image_contents=False):
        if self[item_path][self.COL_INC]:
            return

        item_name = self[item_path][self.COL_NAME]
        item_deps = self[item_path][self.COL_DEPS]

        self[item_path][self.COL_INC] = True
        self.emit("selected-recipes-changed")

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
                dep_included = self[dep_path][self.COL_INC]

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
        if not self[item_path][self.COL_INC]:
            return

        self[item_path][self.COL_INC] = False
        self.emit("selected-recipes-changed")
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

    """
    Find the model path for the item_name
    Returns the path in the model or None
    """
    def find_path_for_item(self, item_name):
        if self.non_target_name(item_name) or item_name not in self.pn_path.keys():
            return None
        else:
            return self.pn_path[item_name]

    def reset(self):
        it = self.get_iter_first()
        while it:
            self.set(it,
                     self.COL_INC, False,
                     self.COL_BINB, "",
                     self.COL_IMG, False)
            it = self.iter_next(it)
        self.emit("selected-recipes-changed")

    """
    Returns two lists. One of user selected recipes and the other containing
    all selected recipes
    """
    def get_selected_recipes(self):
        allrecipes = []
        userrecipes = []

        it = self.get_iter_first()
        while it:
            if self.get_value(it, self.COL_INC):
                name = self.get_value(it, self.COL_NAME)
                type = self.get_value(it, self.COL_TYPE)
                if type != "image":
                    allrecipes.append(name)
                    sel = "User Selected" in self.get_value(it, self.COL_BINB)
                    if sel:
                        userrecipes.append(name)
            it = self.iter_next(it)

        return list(set(userrecipes)), list(set(allrecipes))

    def set_selected_image(self, img):
        self.selected_image = img
        path = self.find_path_for_item(img)
        self.include_item(item_path=path,
                          binb="User Selected",
                          image_contents=True)

    def set_selected_recipes(self, recipelist):
        for pn in recipelist:
            if pn in self.pn_path.keys():
                path = self.pn_path[pn]
                self.include_item(item_path=path,
                                  binb="User Selected")

class RecipeSelection (gtk.Window):

    __dummy_image__ = "--select a base image--"

    __gsignals__ = {
        "recipe-selection-reset" : (gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,
                                    ()),
    }
    def __init__(self, recipemodel, handler):
        gtk.Window.__init__(self)
        self.recipe_model = recipemodel
        self.selected_image = []
        self.image_install = []
        self.selected_recipes = []
        self.last_selected_recipes = []

        self.recipe_model.connect("selected-recipes-changed", self.selected_recipes_changed_cb)

        self.dialog_status = False

    def selected_recipes_changed_cb(self, model):
        _, self.selected_recipes = self.recipe_model.get_selected_recipes()
        if self.dialog_status:
            self.expand.set_label("Selected %s recipes" % len(self.selected_recipes))
            self.add_selected_recipes(self.recipe_model, self.recipe_buffer)

    def save_last_selected_recipes(self):
        self.last_selected_recipes = self.selected_recipes[:len(self.selected_recipes)]

    def clear_last_selected_recipes(self):
        self.last_selected_recipes = []

    def update_recipe_model(self):
        # We want the recipes model to be alphabetised and sortable so create
        # a TreeModelSort to use in the view
        recipesaz_model = gtk.TreeModelSort(self.recipe_model.recipes_model())
        recipesaz_model.set_sort_column_id(self.recipe_model.COL_NAME, gtk.SORT_ASCENDING)
        recipesaz_model.set_default_sort_func(None)
        self.recipesaz_tree.set_model(recipesaz_model)
        self.tasks_tree.set_model(self.recipe_model.tasks_model())
        mlrecipesaz_model = gtk.TreeModelSort(self.recipe_model.mlrecipes_model())
        mlrecipesaz_model.set_sort_column_id(self.recipe_model.COL_NAME, gtk.SORT_ASCENDING)
        mlrecipesaz_model.set_default_sort_func(None)
        self.mlrecipesaz_tree.set_model(self.recipe_model.mlrecipes_model())
        self.mltasks_tree.set_model(self.recipe_model.mltasks_model())

        self.expand.set_label("Selected %s recipes" % len(self.selected_recipes))
        self.add_selected_recipes(self.recipe_model, self.recipe_buffer)

    def reset_clicked_cb(self, tbutton):
        self.selected_image = None
        self.selected_recipes = None
        self.recipe_model.reset()
        self.emit("recipe-selection-reset")
        self.clear_last_selected_recipes()

    def recipesaz_cell3_toggled_cb(self, cell, path, tree):
        self.save_last_selected_recipes()
        HobWidget.toggle_selection_include_cb(cell, path, self, tree, self.recipe_model)

    def recipesaz(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.recipesaz_tree = gtk.TreeView()
        self.recipesaz_tree.set_headers_visible(True)
        self.recipesaz_tree.set_headers_clickable(True)
        self.recipesaz_tree.set_enable_search(True)
        self.recipesaz_tree.set_search_column(0)
        self.recipesaz_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe')
        col.set_clickable(True)
        col.set_resizable(True)
        col.set_sort_column_id(self.recipe_model.COL_NAME)
        col.set_min_width(100)
        col.set_max_width(400)
        col1 = gtk.TreeViewColumn('License')
        col1.set_resizable(True)
        col1.set_clickable(True)
        col1.set_sort_column_id(self.recipe_model.COL_LIC)
        col1.set_min_width(100)
        col1.set_max_width(200)
        col2 = gtk.TreeViewColumn('Group')
        col2.set_clickable(True)
        col2.set_resizable(True)
        col2.set_sort_column_id(self.recipe_model.COL_GROUP)
        col2.set_min_width(100)
        col2.set_max_width(200)
        col3 = gtk.TreeViewColumn('Included')
        col3.set_clickable(True)
        col3.set_resizable(True)
        col3.set_min_width(50)
        col3.set_max_width(50)
        col3.set_sort_column_id(self.recipe_model.COL_INC)

        self.recipesaz_tree.append_column(col)
        self.recipesaz_tree.append_column(col1)
        self.recipesaz_tree.append_column(col2)
        self.recipesaz_tree.append_column(col3)
        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 20)
        cell2 = gtk.CellRendererText()
        cell3 = gtk.CellRendererToggle()
        cell3.set_property('activatable', True)
        cell3.connect("toggled", self.recipesaz_cell3_toggled_cb, self.recipesaz_tree)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_start(cell2, True)
        col3.pack_end(cell3, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_LIC)
        col2.set_attributes(cell2, text=self.recipe_model.COL_GROUP)
        col3.set_attributes(cell3, active=self.recipe_model.COL_INC)

        self.recipesaz_tree.show()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.recipesaz_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 5)
        hb.show()
        self.search = gtk.Entry()
        self.search.show()
        self.recipesaz_tree.set_search_entry(self.search)
        hb.pack_end(self.search, False, False, 0)

        label = gtk.Label("Search:")
        label.show()
        hb.pack_end(label, False, False, 6)

        button = gtk.Button("Reset")
        button.connect('clicked', self.reset_clicked_cb)
        hb.pack_start(button, False, False, 0)

        vbox.pack_start(hb, False, False, 0)

        return vbox


    def mlrecipesaz(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.mlrecipesaz_tree = gtk.TreeView()
        self.mlrecipesaz_tree.set_headers_visible(True)
        self.mlrecipesaz_tree.set_headers_clickable(True)
        self.mlrecipesaz_tree.set_enable_search(True)
        self.mlrecipesaz_tree.set_search_column(0)
        self.mlrecipesaz_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe')
        col.set_clickable(True)
        col.set_resizable(True)
        col.set_sort_column_id(self.recipe_model.COL_NAME)
        col.set_min_width(100)
        col.set_max_width(400)
        col1 = gtk.TreeViewColumn('License')
        col1.set_resizable(True)
        col1.set_clickable(True)
        col1.set_sort_column_id(self.recipe_model.COL_LIC)
        col1.set_min_width(100)
        col1.set_max_width(200)
        col2 = gtk.TreeViewColumn('Group')
        col2.set_clickable(True)
        col2.set_resizable(True)
        col2.set_sort_column_id(self.recipe_model.COL_GROUP)
        col2.set_min_width(100)
        col2.set_max_width(200)
        col3 = gtk.TreeViewColumn('Included')
        col3.set_clickable(True)
        col3.set_resizable(True)
        col3.set_min_width(50)
        col3.set_max_width(50)
        col3.set_sort_column_id(self.recipe_model.COL_INC)

        self.mlrecipesaz_tree.append_column(col)
        self.mlrecipesaz_tree.append_column(col1)
        self.mlrecipesaz_tree.append_column(col2)
        self.mlrecipesaz_tree.append_column(col3)
        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell1.set_property('width-chars', 20)
        cell2 = gtk.CellRendererText()
        cell3 = gtk.CellRendererToggle()
        cell3.set_property('activatable', True)
        cell3.connect("toggled", self.recipesaz_cell3_toggled_cb, self.mlrecipesaz_tree)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_start(cell2, True)
        col3.pack_end(cell3, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_LIC)
        col2.set_attributes(cell2, text=self.recipe_model.COL_GROUP)
        col3.set_attributes(cell3, active=self.recipe_model.COL_INC)

        self.mlrecipesaz_tree.show()

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.mlrecipesaz_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 5)
        hb.show()
        self.search = gtk.Entry()
        self.search.show()
        self.mlrecipesaz_tree.set_search_entry(self.search)
        hb.pack_end(self.search, False, False, 0)

        label = gtk.Label("Search:")
        label.show()
        hb.pack_end(label, False, False, 6)

        button = gtk.Button("Reset")
        button.connect('clicked', self.reset_clicked_cb)
        hb.pack_start(button, False, False, 0)

        vbox.pack_start(hb, False, False, 0)

        return vbox

    def tasks_cell2_toggled_cb(self, cell, path, tree):
        self.save_last_selected_recipes()
        HobWidget.toggle_include_cb(cell, path, self, tree, self.recipe_model)

    def tasks(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.tasks_tree = gtk.TreeView()
        self.tasks_tree.set_headers_visible(True)
        self.tasks_tree.set_headers_clickable(False)
        self.tasks_tree.set_enable_search(True)
        self.tasks_tree.set_search_column(0)
        self.tasks_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe Collection')
        col.set_clickable(True)
        col.set_resizable(True)
        col.set_min_width(100)
        col.set_max_width(400)
        col.set_sort_column_id(self.recipe_model.COL_NAME)
        col1 = gtk.TreeViewColumn('Description')
        col1.set_clickable(True)
        col1.set_resizable(True)
        col1.set_min_width(100)
        col1.set_max_width(200)
        col1.set_sort_column_id(self.recipe_model.COL_DESC)
        col2 = gtk.TreeViewColumn('Include')
        col2.set_clickable(True)
        col2.set_resizable(True)
        col2.set_min_width(50)
        col2.set_max_width(50)
        col2.set_sort_column_id(self.recipe_model.COL_INC)

        self.tasks_tree.append_column(col)
        self.tasks_tree.append_column(col1)
        self.tasks_tree.append_column(col2)

        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererToggle()
        cell2.set_property('activatable', True)
        cell2.connect("toggled", self.tasks_cell2_toggled_cb, self.tasks_tree)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_end(cell2, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_DESC)
        col2.set_attributes(cell2, active=self.recipe_model.COL_INC)

        self.tasks_tree.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.tasks_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 0)
        hb.show()
        search = gtk.Entry()
        search.show()
        self.tasks_tree.set_search_entry(search)
        hb.pack_end(search, False, False, 0)
        label = gtk.Label("Search:")
        label.show()
        hb.pack_end(label, False, False, 6)

        button = gtk.Button("Reset")
        button.connect('clicked', self.reset_clicked_cb)
        hb.pack_start(button, False, False, 0)

        vbox.pack_start(hb, False, False, 0)

        return vbox

    def mltasks(self):
        vbox = gtk.VBox(False, 6)
        vbox.show()
        self.mltasks_tree = gtk.TreeView()
        self.mltasks_tree.set_headers_visible(True)
        self.mltasks_tree.set_headers_clickable(False)
        self.mltasks_tree.set_enable_search(True)
        self.mltasks_tree.set_search_column(0)
        self.mltasks_tree.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col = gtk.TreeViewColumn('Recipe Collection')
        col.set_clickable(True)
        col.set_resizable(True)
        col.set_min_width(100)
        col.set_max_width(250)
        col.set_sort_column_id(self.recipe_model.COL_NAME)
        col1 = gtk.TreeViewColumn('Description')
        col1.set_clickable(True)
        col1.set_resizable(True)
        col1.set_min_width(100)
        col1.set_max_width(200)
        col1.set_sort_column_id(self.recipe_model.COL_DESC)
        col2 = gtk.TreeViewColumn('Include')
        col2.set_clickable(True)
        col2.set_resizable(True)
        col2.set_min_width(60)
        col2.set_max_width(60)
        col2.set_sort_column_id(self.recipe_model.COL_INC)

        self.mltasks_tree.append_column(col)
        self.mltasks_tree.append_column(col1)
        self.mltasks_tree.append_column(col2)

        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()
        cell2 = gtk.CellRendererToggle()
        cell2.set_property('activatable', True)
        cell2.connect("toggled", self.tasks_cell2_toggled_cb, self.mltasks_tree)

        col.pack_start(cell, True)
        col1.pack_start(cell1, True)
        col2.pack_end(cell2, True)

        col.set_attributes(cell, text=self.recipe_model.COL_NAME)
        col1.set_attributes(cell1, text=self.recipe_model.COL_DESC)
        col2.set_attributes(cell2, active=self.recipe_model.COL_INC)

        self.mltasks_tree.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.mltasks_tree)
        vbox.pack_start(scroll, True, True, 0)

        hb = gtk.HBox(False, 0)
        hb.show()
        search = gtk.Entry()
        search.show()
        self.mltasks_tree.set_search_entry(search)
        hb.pack_end(search, False, False, 0)
        label = gtk.Label("Search:")
        label.show()
        hb.pack_end(label, False, False, 6)

        button = gtk.Button("Reset")
        button.connect('clicked', self.reset_clicked_cb)
        hb.pack_start(button, False, False, 0)

        vbox.pack_start(hb, False, False, 0)

        return vbox

    def show_binb_info(self, model, path, parent):
        it = model.get_iter(path)
        binb = model.get_value(it, model.COL_BINB)
        w = gtk.MessageDialog(parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "Brought in by: " + binb)
        w.run()
        w.destroy()

    def selection_clicked_cb(self, textview, event, model):
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        recipe_buffer = textview.get_buffer()
        x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
        it = textview.get_iter_at_location(x, y)

        tags = it.get_tags()
        for tag in tags:
            path = tag.get_data("path")
            if path != 0:
                window = textview.get_toplevel()
                self.show_binb_info(model, path, window)
                break

        return False

    def insert_text_with_tag(self, recipe_buffer, it, text, path, highlight=False):
        if highlight:
            tag = recipe_buffer.create_tag(None, foreground="blue", background="yellow")
        else:
            tag = recipe_buffer.create_tag(None, foreground="blue")
        tag.set_data("path", path)
        recipe_buffer.insert_with_tags(it, text, tag)

    def add_selected_recipes(self, model, recipe_buffer):
        recipe_buffer.set_text("")
        for i in self.selected_recipes:
            path = model.pn_path[i]
            tit = recipe_buffer.get_end_iter()
            if i in self.last_selected_recipes:
                self.insert_text_with_tag(recipe_buffer, tit, i + "  ", path)
            else:
                self.insert_text_with_tag(recipe_buffer, tit, i + "  ", path, True)

    def motion_cb(self, textview, event):
        x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
        it = textview.get_iter_at_location(x, y)
        if it.get_tags():
            textview.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        else:
            textview.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))

    def selections(self):
        vbox = gtk.VBox(False, 5)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        vbox.add(scroll)

        self.expand = gtk.Expander("Selected Recipes")
        self.expand.set_expanded(True)
        scroll.add_with_viewport(self.expand)

        tv = gtk.TextView()
        tv.set_editable(False)
        tv.set_wrap_mode(gtk.WRAP_WORD)
        tv.set_cursor_visible(False)
        self.recipe_buffer = gtk.TextBuffer()
        tv.set_buffer(self.recipe_buffer)
        tv.connect("event-after", self.selection_clicked_cb, self.recipe_model)
        tv.connect("motion-notify-event", self.motion_cb)
        self.expand.add(tv)

        return vbox

    def main(self, button):
        window = gtk.Dialog("Recipe List", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        window.set_size_request(800, 600)
        window.set_border_width(5)

        table = gtk.Table(10, 10, True)
        table.set_col_spacings(3)
        window.vbox.add(table)

        ins = gtk.Notebook()
        ins.set_show_tabs(True)
        label = gtk.Label("Recipes")
        ins.append_page(self.recipesaz(), tab_label=label)
        label = gtk.Label("Recipe Collections")
        ins.append_page(self.tasks(), tab_label=label)

        label = gtk.Label("Multilib Recipes")
        ins.append_page(self.mlrecipesaz(), tab_label=label)
        label = gtk.Label("Multilib Recipe Collections")
        ins.append_page(self.mltasks(), tab_label=label)

        ins.set_current_page(0)
        table.attach(ins, 0, 7, 0, 10, gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)

        selections = self.selections()
        table.attach(selections, 7, 10, 0, 10, gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)        

        self.update_recipe_model()

        window.show_all()
        self.dialog_status = True
        response = window.run()
        self.dialog_status = False
        window.destroy()

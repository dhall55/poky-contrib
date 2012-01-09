#!/usr/bin/env python
#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao Xu <dongxiao.xu@intel.com>
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

import glib
import gobject
import gtk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    import bb
except RuntimeError as exc:
    sys.exit(str(exc))

from bb.ui import uihelper
from bb.ui.crumbs.recipelistmodel import RecipeListModel, RecipeSelection
from bb.ui.crumbs.packagelistmodel import PackageListModel, PackageSelection
from bb.ui.crumbs.hobeventhandler import HobHandler
from bb.ui.crumbs.hig import CrumbsDialog
from bb.ui.crumbs.runningbuild import RunningBuildTreeView, RunningBuild
from bb.ui.crumbs.template import TemplateMgr
from bb.ui.crumbs.layerselection import LayerSelection
from bb.ui.crumbs.advancedsetting import AdvancedSetting
from bb.ui.crumbs.progressbar import HobProgressBar
from bb.ui.crumbs.progressbar import Case
from bb.ui.crumbs.progressbar import ComplexHobProgressBar
from bb.ui.crumbs.hobwidget import HobWidget
from bb.ui.crumbs.hobcolors import HobColors
import xmlrpclib
import logging
import Queue
import string

(MACHINE_SELECTION, RECIPE_GENERATING, RECIPE_GENERATED, PACKAGE_GENERATING, PACKAGE_GENERATED, FAST_IMAGE_GENERATING, IMAGE_GENERATING, IMAGE_GENERATED) = range(8)

class MainWindow (gtk.Window):

    __dummy_machine__ = "--select a machine--"

    def __init__(self, split_model, recipemodel, packagemodel, handler, params):
        gtk.Window.__init__(self)
        # global state
        self.split_model = split_model
        self.curr_mach = None
        self.all_mach = None
        self.image_addr = params["image_addr"]
        self.generating = False
        self.build_succeeded = True
        self.stopping = False
        self.current_step = None

        self.advanced_setting = AdvancedSetting(self.split_model, params)
        self.advanced_setting.connect("need-reparse", self.need_reparse_cb)
        self.layer_selection = LayerSelection(self.split_model, handler, params)

        self.recipe_model = recipemodel
        self.recipe_model.connect("recipelist-populated", self.recipe_ready_cb)
        self.recipe_selection = RecipeSelection(recipemodel, handler)
        self.recipe_selection.connect("recipe-selection-reset", self.recipe_reset_cb)

        self.package_model = packagemodel
        self.package_model.connect("packagelist-populated", self.package_ready_cb)
        self.package_selection = PackageSelection(packagemodel, handler)

        self.handler = handler

        self.connect("delete-event", self.destroy_window)
        self.set_title("HOB")
        self.set_icon_name("applications-development")
        self.set_size_request(700, 650)

        self.build = RunningBuild(sequential=True)
        self.build.connect("build-failed", self.running_build_failed_cb)
        self.build.connect("build-succeeded", self.running_build_succeeded_cb)
        self.build.connect("build-started", self.build_started_cb)
        self.build.connect("build-complete", self.build_complete_cb)

        self.vbox = gtk.VBox(False, 15)
        self.vbox.set_border_width(50)
        self.vbox.show()
        self.add(self.vbox)
        self.config_top_button = self.create_config_top_button()
        self.config_machine = self.create_config_machine()
        self.config_baseimg = self.create_config_baseimg()
        self.config_build_button = self.create_config_build_button()

        self.create_recipe_progress = ComplexHobProgressBar()
        # a possibility is when doing RECIPE_GENERATING, events include "ParseXXX"es and "TreeDataPreparationXXX"es.
        case = Case([[0.5, 0.5]])
        case.append_step(RECIPE_GENERATING)
        case.append_event(("ParseStarted", "ParseProgress", "ParseCompleted"))
        case.append_event(("TreeDataPreparationStarted", "TreeDataPreparationProgress", "TreeDataPreparationCompleted"))
        self.create_recipe_progress.add_case(case)
        # another possibility is when doing RECIPE_GENERATING, that are "CacheLoadXXX"es rather than "ParseXXX"es.
        case = Case([[0.3, 0.7]])
        case.append_step(RECIPE_GENERATING)
        case.append_event(("CacheLoadStarted", "CacheLoadProgress", "CacheLoadCompleted"))
        case.append_event(("TreeDataPreparationStarted", "TreeDataPreparationProgress", "TreeDataPreparationCompleted"))
        self.create_recipe_progress.add_case(case)
        # set stepid because RECIPE_GENERATING is the only one
        # we leave set_case_by_num to the event handler when the first event arrives
        # and determine according to whether it is ParseXXX or CacheLoadXXX.
        self.create_recipe_progress.set_stepid(RECIPE_GENERATING)

        self.create_build_progress = self.create_build_progress()
        self.create_image_address = self.create_image_address()
        self.package_button, self.package_label = self.create_config_package()

        self.switch_page(MACHINE_SELECTION)
        self.tmpmgr = TemplateMgr()

    def _remove_all_widget(self):
        self.vbox.remove(self.create_recipe_progress)
        self.vbox.remove(self.create_build_progress)
        self.vbox.remove(self.config_top_button)
        self.vbox.remove(self.config_baseimg)
        self.vbox.remove(self.config_machine)
        self.vbox.remove(self.config_build_button)
        self.vbox.remove(self.create_image_address)
        table_baseimg = self.config_baseimg.get_children()[0].get_children()[0].get_children()[0]
        table_baseimg.remove(self.package_button)
        table_baseimg.remove(self.package_label)

    def switch_page(self, next_step):
        self._remove_all_widget()
        if next_step == MACHINE_SELECTION:
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
        elif next_step == RECIPE_GENERATING:
            self.create_recipe_progress.reset()
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.create_recipe_progress, expand=False, fill=False)
        elif next_step == RECIPE_GENERATED:
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.config_baseimg, expand=False, fill=False)
            self.vbox.pack_end(self.config_build_button, expand=False, fill=False)
        elif next_step == PACKAGE_GENERATED:
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.config_baseimg, expand=False, fill=False)
            self.vbox.pack_end(self.config_build_button, expand=False, fill=False)
            table_baseimg = self.config_baseimg.get_children()[0].get_children()[0].get_children()[0]
            table_baseimg.attach(self.package_button, 14, 16, 5, 7)
            table_baseimg.attach(self.package_label, 16, 19, 5, 9)
        elif next_step == PACKAGE_GENERATING or next_step == FAST_IMAGE_GENERATING:
            self.view_build_progress.reset()
            # set_case_by_num and set_stepid
            if next_step == PACKAGE_GENERATING:
                self.view_build_progress.set_case_by_num(1)
            else:
                self.view_build_progress.set_case_by_num(0)
            self.view_build_progress.set_stepid(next_step, "Recipe build tasks: ")
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.config_baseimg, expand=False, fill=False)
            self.vbox.pack_start(self.create_build_progress, expand=False, fill=False)
            self.vbox.pack_end(self.config_build_button, expand=False, fill=False)
        elif next_step == IMAGE_GENERATING:
            self.view_build_progress.reset()
            if self.current_step == PACKAGE_GENERATED:
                self.view_build_progress.set_case_by_num(2)
            self.view_build_progress.set_stepid(next_step, "Image rootfs tasks: ")
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.config_baseimg, expand=False, fill=False)
            self.vbox.pack_start(self.create_build_progress, expand=False, fill=False)
            self.vbox.pack_end(self.config_build_button, expand=False, fill=False)
            table_baseimg = self.config_baseimg.get_children()[0].get_children()[0].get_children()[0]
            table_baseimg.attach(self.package_button, 14, 16, 5, 7)
            table_baseimg.attach(self.package_label, 16, 19, 5, 9)
        elif next_step == IMAGE_GENERATED:
            self.vbox.pack_start(self.config_top_button, expand=False, fill=False)
            self.vbox.pack_start(self.config_machine, expand=False, fill=False)
            self.vbox.pack_start(self.config_baseimg, expand=False, fill=False)
            self.vbox.pack_start(self.create_image_address, expand=False, fill=False)
            self.vbox.pack_end(self.config_build_button, expand=False, fill=False)

        self.current_step = next_step
        self.vbox.show_all()

    def update_machines(self, handler, machines):
        self.all_mach = machines
        model = self.machine_combo.get_model()
        if model:
            model.clear()

        self.machine_combo.append_text(MainWindow.__dummy_machine__)
        for machine in machines:
            self.machine_combo.append_text(machine)
        self.machine_combo.set_active(0)

    def machine_combo_changed_cb(self, machine_combo):
        combo_item = machine_combo.get_active_text()
        if combo_item == self.__dummy_machine__:
            self.switch_page(MACHINE_SELECTION)
        else:
            self.curr_mach = combo_item
            self.set_user_config()
            self.handler.generate_recipes()
            self.switch_page(RECIPE_GENERATING)

    def image_changed_cb(self, combo):
        if self.image_combo.get_active_text() == self.recipe_selection.__dummy_image__:
            return
        window = self.image_combo.get_toplevel()
        model = self.image_combo.get_model()
        it = self.image_combo.get_active_iter()
        if it:
            path = model.get_path(it)
            # Firstly, deselect the previous image
            userp, _ = self.recipe_model.get_selected_recipes()
            self.recipe_model.reset()
            # Now select the new image and save its path in case we
            # change the image later
            HobWidget.toggle_item(window, path, model, self.recipe_model, image=True)
            if len(userp):
                self.recipe_model.set_selected_recipes(userp)

            self.recipe_selection.selected_image = model[path][self.recipe_model.COL_NAME]
            self.image_install = model[path][self.recipe_model.COL_INSTALL]
            self.package_selection.selected_packages = (self.image_install or "").split()
            self.switch_page(RECIPE_GENERATED)

    def update_image_model(self):
        self.image_combo.set_model(self.recipe_model.images_model())
        self.image_combo.set_active(0)

        if not self.image_combo_id:
            self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)

        if self.recipe_selection.selected_image:
            if self.image_combo_id:
                self.image_combo.disconnect(self.image_combo_id)
                self.image_combo_id = None
            self.recipe_model.set_selected_image(self.recipe_selection.selected_image)

            cnt = 0
            it = self.recipe_model.images.get_iter_first()
            while it:
                path = self.recipe_model.images.get_path(it)
                if self.recipe_model.images[path][self.recipe_model.COL_NAME] == self.recipe_selection.selected_image:
                    self.image_combo.set_active(cnt)
                    break
                it = self.recipe_model.images.iter_next(it)
                cnt = cnt + 1
            
            if not self.image_combo_id:
                self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)

        if self.recipe_selection.selected_recipes:
            self.recipe_model.set_selected_recipes(self.recipe_selection.selected_recipes)


    def set_user_config(self):
        self.handler.init_cooker()
        self.handler.set_bblayers(self.layer_selection.layers)
        self.handler.set_machine(self.curr_mach)
        self.handler.set_package_format(self.advanced_setting.curr_package_format)
        self.handler.set_distro(self.advanced_setting.curr_distro)
        self.handler.set_dl_dir(self.advanced_setting.dldir)
        self.handler.set_sstate_dir(self.advanced_setting.sstatedir)
        self.handler.set_sstate_mirror(self.advanced_setting.sstatemirror)
        self.handler.set_pmake(self.advanced_setting.pmake)
        self.handler.set_bbthreads(self.advanced_setting.bbthread)
        self.handler.set_extra_size(self.advanced_setting.image_extra_size)
        self.handler.set_incompatible_license(self.advanced_setting.incompat_license)
        self.handler.set_sdk_machine(self.advanced_setting.curr_sdk_machine)
        self.handler.set_extra_config(self.advanced_setting.extra_setting)
        self.handler.set_extra_inherit("packageinfo")

    def set_busy_cursor(self, busy=True):
        """
        Convenience method to set the cursor to a spinner when executing
        a potentially lengthy process.
        A busy value of False will set the cursor back to the default
        left pointer.
        """
        if busy:
            cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        else:
            # TODO: presumably the default cursor is different on RTL
            # systems. Can we determine the default cursor? Or at least
            # the cursor which is set before we change it?
            cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        window = self.get_root_window()
        window.set_cursor(cursor)

    def busy(self, handler):
        self.generating = True
        self.set_busy_cursor()
        if self.image_combo_id:
            self.image_combo.disconnect(self.image_combo_id)
            self.image_combo_id = None
        self.disable_widgets()

    def data_generated(self, handler):
        self.generating = False
        self.enable_widgets()
        if not self.image_combo_id:
            self.image_combo_id = self.image_combo.connect("changed", self.image_changed_cb)
        self.set_busy_cursor(False)

    def command_succeeded(self, handler, initcmd):
        if initcmd == self.handler.LAYERS_REFRESH:
            self.layer_refreshed()


    def command_failed(self, handler, msg):
        lbl = "<b>Error</b>\n"
        lbl = lbl + "%s\n\n" % msg
        dialog = CrumbsDialog(self, lbl, gtk.STOCK_DIALOG_WARNING)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        response = dialog.run()
        dialog.destroy()
        self.handler.clear_busy()

    def enable_widgets(self):
        self.config_top_button.set_sensitive(True)
        self.config_machine.set_sensitive(True)
        self.config_baseimg.set_sensitive(True)
        self.config_build_button.set_sensitive(True)

    def disable_widgets(self):
        self.config_top_button.set_sensitive(False)
        self.config_machine.set_sensitive(False)
        self.config_baseimg.set_sensitive(False)
        self.config_build_button.set_sensitive(False)

    def load_template(self, path):
        self.tmpmgr.load(path)

        # bblayers.conf
        layers = self.tmpmgr.getVar("BBLAYERS").split()

        lbl = "<b>Error</b>\nError in loading template because "
        lbl += "some layer in the template is not exist in all available layers"

        if self.split_model:
            if not set(layers) <= set(self.layer_selection.layers_avail):
                HobWidget.conf_error(self, lbl)
                return
        else:
            for layer in layers:
                if not os.path.exists(layer+'/conf/layer.conf'):
                    HobWidget.conf_error(self, lbl)
                    return

        self.layer_selection.layers = layers

        self.curr_mach = self.tmpmgr.getVar("MACHINE")
        self.advanced_setting.curr_package_format = " ".join(self.tmpmgr.getVar("PACKAGE_CLASSES").split("package_"))
        self.advanced_setting.curr_distro = self.tmpmgr.getVar("DISTRO")
        self.advanced_setting.dldir = self.tmpmgr.getVar("DL_DIR")
        self.advanced_setting.sstatedir = self.tmpmgr.getVar("SSTATE_DIR")
        self.advanced_setting.sstatemirror = self.tmpmgr.getVar("SSTATE_MIRROR")
        self.advanced_setting.pmake = int(self.tmpmgr.getVar("PARALLEL_MAKE").split()[1])
        self.advanced_setting.bbthread = int(self.tmpmgr.getVar("BB_NUMBER_THREAD"))
        self.advanced_setting.image_extra_size = int(self.tmpmgr.getVar("IMAGE_EXTRA_SPACE"))
        self.advanced_setting.incompat_license = self.tmpmgr.getVar("INCOMPATIBLE_LICENSE")
        self.advanced_setting.curr_sdk_machine = self.tmpmgr.getVar("SDKMACHINE")
        self.advanced_setting.extra_setting = eval(self.tmpmgr.getVar("EXTRA_SETTING"))
        self.advanced_setting.toolchain_build = eval(self.tmpmgr.getVar("TOOLCHAIN_BUILD"))

        # image.bb
        self.recipe_selection.selected_image = self.tmpmgr.getVar("__SELECTED_IMAGE__")
        self.recipe_selection.selected_recipes = self.tmpmgr.getVar("DEPENDS").split()
        self.package_selection.selected_packages = self.tmpmgr.getVar("IMAGE_INSTALL").split()

        self.handler.layer_refresh(self.layer_selection.layers)
        self.tmpmgr.destroy()

    def layer_refreshed(self):
        model = self.machine_combo.get_model()
        active = 0
        while active < len(model):
            if model[active][0] == self.curr_mach:
                self.machine_combo.set_active(active)
                break
            active += 1

    def config_load_clicked_cb(self, button):
        dialog = gtk.FileChooserDialog("Load Template Files", self,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_OPEN, gtk.RESPONSE_YES,
                                       gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        filter = gtk.FileFilter()
        filter.set_name("HOB Files")
        filter.add_pattern("*.hob")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.load_template(path)
        dialog.destroy()

    def cancel_build_cb(self, button):
        if self.stopping:
            lbl = "<b>Force Stop build?</b>\nYou've already selected Stop once,"
            lbl = lbl + " would you like to 'Force Stop' the build?\n\n"
            lbl = lbl + "This will stop the build as quickly as possible but may"
            lbl = lbl + " well leave your build directory in an  unusable state"
            lbl = lbl + " that requires manual steps to fix.\n"
            dialog = CrumbsDialog(self, lbl, gtk.STOCK_DIALOG_WARNING)
            dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            dialog.add_button("Force Stop", gtk.RESPONSE_YES)
        else:
            lbl = "<b>Stop build?</b>\n\nAre you sure you want to stop this"
            lbl = lbl + " build?\n\n'Force Stop' will stop the build as quickly as"
            lbl = lbl + " possible but may well leave your build directory in an"
            lbl = lbl + " unusable state that requires manual steps to fix.\n\n"
            lbl = lbl + "'Stop' will stop the build as soon as all in"
            lbl = lbl + " progress build tasks are finished. However if a"
            lbl = lbl + " lengthy compilation phase is in progress this may take"
            lbl = lbl + " some time."
            dialog = CrumbsDialog(self, lbl, gtk.STOCK_DIALOG_WARNING)
            dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            dialog.add_button("Stop", gtk.RESPONSE_OK)
            dialog.add_button("Force Stop", gtk.RESPONSE_YES)
        response = dialog.run()
        dialog.destroy()
        if response != gtk.RESPONSE_CANCEL:
            self.stopping = True
        if response == gtk.RESPONSE_OK:
            self.handler.cancel_build()
        elif response == gtk.RESPONSE_YES:
            self.handler.cancel_build(True)

    def save_template(self, path):
        self.tmpmgr.open(path)

        # bblayers.conf
        self.tmpmgr.setVar("BBLAYERS", " ".join(self.layer_selection.layers))

        # local.conf
        self.tmpmgr.setVar("MACHINE", self.curr_mach)
        self.tmpmgr.setVar("DISTRO", self.advanced_setting.curr_distro)
        self.tmpmgr.setVar("DL_DIR", self.advanced_setting.dldir)
        self.tmpmgr.setVar("SSTATE_DIR", self.advanced_setting.sstatedir)
        self.tmpmgr.setVar("SSTATE_MIRROR", self.advanced_setting.sstatemirror)
        self.tmpmgr.setVar("PARALLEL_MAKE", "-j %s" % self.advanced_setting.pmake)
        self.tmpmgr.setVar("BB_NUMBER_THREAD", self.advanced_setting.bbthread)
        self.tmpmgr.setVar("PACKAGE_CLASSES", " ".join(["package_" + i for i in self.advanced_setting.curr_package_format.split()]))
        self.tmpmgr.setVar("IMAGE_EXTRA_SPACE", self.advanced_setting.image_extra_size)
        self.tmpmgr.setVar("INCOMPATIBLE_LICENSE", self.advanced_setting.incompat_license)
        self.tmpmgr.setVar("SDKMACHINE", self.advanced_setting.curr_sdk_machine)
        self.tmpmgr.setVar("EXTRA_SETTING", self.advanced_setting.extra_setting)
        self.tmpmgr.setVar("TOOLCHAIN_BUILD", self.advanced_setting.toolchain_build)

        # image.bb
        _, all_recipes = self.recipe_model.get_selected_recipes()
        self.tmpmgr.setVar("DEPENDS", all_recipes)
        all_packages = self.package_model.get_selected_packages() or self.recipe_selection.image_install
        self.tmpmgr.setVar("IMAGE_INSTALL", all_packages)

        # misc
        self.tmpmgr.setVar("__SELECTED_IMAGE__", self.recipe_selection.selected_image)

        self.tmpmgr.save()
        self.tmpmgr.destroy()

    def recipe_save_clicked_cb(self, button):
        dialog = gtk.FileChooserDialog("Save Template Files", self,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_SAVE, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        dialog.set_current_name("hob")
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.save_template(path)
        dialog.destroy()

    def generate_packages(self, button, url):
        # If no base image and no selected packages don't build anything
        user_recipes, all_recipes = self.recipe_model.get_selected_recipes()
        if not self.recipe_selection.selected_image and not user_recipes and not all_recipes:
            lbl = "<b>No selections made</b>\nYou have not made any selections"
            lbl = lbl + " so there isn't anything to bake at this time."
            dialog = CrumbsDialog(self, lbl, gtk.STOCK_DIALOG_INFO)
            dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            dialog.run()
            dialog.destroy()
            return

        self.switch_page(PACKAGE_GENERATING)
        self.build.reset()
        self.package_model.clear()

        self.set_user_config()
        self.handler.generate_packages(all_recipes)
        return

    def generate_image(self, button):
        _, selected_recipes = self.recipe_model.get_selected_recipes() or []
        selected_packages = self.package_selection.selected_packages or []
        if self.current_step == RECIPE_GENERATED:
            next_step = FAST_IMAGE_GENERATING
            fast_mode = True
        else:
            if self.package_model.get_selected_packages():
                selected_packages = self.package_model.get_selected_packages()
            next_step = IMAGE_GENERATING
            fast_mode = False
        # If no base image and no selected packages don't build anything
        if not selected_recipes or not selected_packages:
            lbl = "<b>No selections made</b>\nYou have not made any selections"
            lbl = lbl + " so there isn't anything to bake at this time."
            dialog = CrumbsDialog(self, lbl, gtk.STOCK_DIALOG_INFO)
            dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            dialog.run()
            dialog.destroy()
            return

        self.set_user_config()
        self.handler.generate_image(selected_recipes, selected_packages, fast_mode, self.advanced_setting.toolchain_build)

        self.switch_page(next_step)
        self.build.reset()
        return


    def build_started_cb(self, running_build):
        self.cancel.set_sensitive(True)
        self.set_busy_cursor(False)

    def build_complete_cb(self, running_build):
        # Have the handler process BB events again
        self.handler.building = False
        self.stopping = False
        self.cancel.set_sensitive(False)
        self.view_build_progress.set_style(self.build_succeeded)

        if self.build_succeeded:
            if self.current_step == IMAGE_GENERATING:
                self.switch_page(IMAGE_GENERATED)
            if self.current_step == FAST_IMAGE_GENERATING:
                self.switch_page(IMAGE_GENERATING)
        else:
            self.handler.build_failed_async()
            if self.current_step == PACKAGE_GENERATING or self.current_step == FAST_IMAGE_GENERATING:
                self.current_step = RECIPE_GENERATED
            elif self.current_step == IMAGE_GENERATING:
                self.current_step = PACKAGE_GENERATED

    def running_build_succeeded_cb(self, running_build):
        self.build_succeeded = True

    def running_build_failed_cb(self, running_build):
        self.build_succeeded = False

    def destroy_window(self, widget, event):
        gtk.main_quit()

    def create_config_top_button(self):
        hbox_top = gtk.HBox(False, 0)

        hbox_button = gtk.HBox(False, 0)
        hbox_button.set_border_width(1)
        hbox_top.pack_end(hbox_button, expand=False, fill=False)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.set_size_request(60, 35)
        hbox_button.pack_end(frame, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.connect("clicked", self.advanced_setting.main)
        frame.add(button)

        hbox_button = gtk.HBox(False, 0)
        hbox_button.set_border_width(1)
        hbox_top.pack_end(hbox_button, expand=False, fill=False)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.set_size_request(60, 35)
        hbox_button.pack_end(frame, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.connect("clicked", self.config_load_clicked_cb)
        frame.add(button)

        hbox_top.show_all()

        return hbox_top

    def create_config_machine(self):
        hbox_machine = gtk.HBox(False, 0)

        aspect_frame = gtk.AspectFrame(label=None, xalign=0.5, yalign=0.5, ratio=4, obey_child=False)
        aspect_frame.set_size_request(600, 150)
        hbox_machine.pack_start(aspect_frame, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 0)
        aspect_frame.add(sub_vbox)

        table_back = gtk.Table(9, 20, False)
        table_back.set_row_spacings(5)
        table_back.set_col_spacings(5)
        sub_vbox.pack_start(table_back, expand=True, fill=False)

        label = gtk.Label()
        label.set_alignment(0, 1.0)
        label.set_markup("<span weight=\"bold\">Select a machine</span>\n")
        table_back.attach(label, 2, 18, 1, 4)

        label = gtk.Label()
        label.set_alignment(0, 0.5)
        label.set_markup("This is the architecture of the target board for which you are building the image.\n")
        table_back.attach(label, 2, 18, 4, 5)

        self.machine_combo = gtk.combo_box_new_text()
        self.machine_combo.connect("changed", self.machine_combo_changed_cb)
        table_back.attach(self.machine_combo, 2, 9, 5, 7)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DND_MULTIPLE, gtk.ICON_SIZE_MENU)
        layer_button = gtk.Button()
        layer_button.set_image(image)
        layer_button.connect("clicked", self.layer_selection.main)
        table_back.attach(layer_button, 9, 11, 5, 7)

        label = gtk.Label()
        label.set_alignment(0, 0.0)
        label.set_markup("<span weight=\"bold\">Layers</span>\n"
                 "Add support for machines, software, etc")
        table_back.attach(label, 11, 14, 5, 9)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CAPS_LOCK_WARNING, gtk.ICON_SIZE_MENU)
        hbox = gtk.HBox()
        hbox.add(image)
        table_back.attach(hbox, 14, 15, 5, 9)

        hbox_machine.show_all()
        
        return hbox_machine

    def create_config_baseimg(self):
        hbox_baseimg = gtk.HBox(False, 0)
        hbox_baseimg.show_all()

        aspect_frame = gtk.AspectFrame(label=None, xalign=0.5, yalign=0.5, ratio=3.33, obey_child=False)
        aspect_frame.set_size_request(600, 180)
        hbox_baseimg.pack_start(aspect_frame, False, False, 0)

        sub_vbox = gtk.VBox(False, 0)
        aspect_frame.add(sub_vbox)

        table_back = gtk.Table(9, 20, False)
        table_back.set_row_spacings(5)
        table_back.set_col_spacings(5)
        sub_vbox.pack_start(table_back, expand=True, fill=False)

        label = gtk.Label()
        label.set_alignment(0, 1.0)
        label.set_markup("<span weight=\"bold\">Select a base image</span>\n")
        table_back.attach(label, 2, 18, 1, 4)

        label = gtk.Label()
        label.set_alignment(0, 0.5)
        label.set_markup("Base images are pre-packaged images we have included to make your life easier.\n\
You can build these images as they are, or customize them to your specific needs.\n")
        table_back.attach(label, 2, 18, 4, 5)

        self.image_combo_id = None
        self.image_combo = gtk.ComboBox()
        image_combo_cell = gtk.CellRendererText()
        self.image_combo.pack_start(image_combo_cell, True)
        self.image_combo.add_attribute(image_combo_cell, 'text', self.recipe_model.COL_NAME)
        self.image_combo.set_add_tearoffs(True)

        table_back.attach(self.image_combo, 2, 9, 5, 7)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.connect("clicked", self.recipe_selection.main)
        table_back.attach(button, 9, 11, 5, 7)

        label = gtk.Label()
        label.set_alignment(0, 0.0)
        label.set_markup("<span weight=\"bold\">View Recipes</span>\n"
                 "Add/remove")
        table_back.attach(label, 11, 14, 5, 9)

        hbox_baseimg.show_all()

        return hbox_baseimg

    def create_config_package(self):
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.connect("clicked", self.package_selection.main)

        label = gtk.Label()
        label.set_alignment(0,0.0)
        label.set_markup("<span weight=\"bold\">View Packages</span>\n"
                 "Add/remove")
        return button, label

    def create_config_build_button(self):
        hbox_button = gtk.HBox(False, 5)
        hbox_button.show_all()
        button = gtk.Button("Build Image")
        button.set_size_request(150, 50)
        button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(HobColors.LIGHT_ORANGE))
        button.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(HobColors.LIGHT_ORANGE))
        button.modify_bg(gtk.STATE_SELECTED, gtk.gdk.Color(HobColors.LIGHT_ORANGE))
        button.set_tooltip_text("Build image to get your target image")
        button.connect("clicked", self.generate_image)
        hbox_button.pack_end(button, expand=False, fill=False)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()

        label = gtk.Label(" or ")
        hbox_button.pack_end(label, expand=False, fill=False)

        if hasattr(gtk, "LinkButton"):
            button = gtk.LinkButton("Build packages first based on recipe selection for late customization on packages for the target image", "Build Packages")
            gtk.link_button_set_uri_hook(self.generate_packages)
        else:
            button = gtk.Button("Build Packages")
            button.connect("clicked", self.generate_packages, "http://www.yoctoproject.org")
        hbox_button.pack_end(button, expand=False, fill=False)
        hbox_button.show_all()
        return hbox_button

    def create_build_progress(self):
        hbox = gtk.HBox(False, 10)
        self.view_build_progress = ComplexHobProgressBar()
        # a possibility is BuildStarted, sceneQueueTaskStarted, runQueueTaskStarted, and BuildCompleted whose indexes are all 0 happen
        # when doing FAST_IMAGE_GENERATING and IMAGE_GENERATING sequently.
        case = Case([[0, 0.27, 0.63, 0], [0, 0.03, 0.07, 0]])
        case.append_step(FAST_IMAGE_GENERATING)
        case.append_step(IMAGE_GENERATING)
        case.append_event(("BuildStarted", ))
        case.append_event(("sceneQueueTaskStarted", ))
        case.append_event(("runQueueTaskStarted", ))
        case.append_event(("BuildCompleted", ))
        self.view_build_progress.add_case(case)
        # another possibility is BuildStarted, sceneQueueTaskStarted, runQueueTaskStarted, and BuildCompleted happen
        # when doing PACKAGE_GENERATING for building packages.
        case = Case([[0, 0.2, 0.8, 0]])
        case.append_step(PACKAGE_GENERATING)
        case.append_event(("BuildStarted", ))
        case.append_event(("sceneQueueTaskStarted", ))
        case.append_event(("runQueueTaskStarted", ))
        case.append_event(("BuildCompleted", ))
        self.view_build_progress.add_case(case)
        # the third possibility is BuildStarted, sceneQueueTaskStarted, runQueueTaskStarted, and BuildCompleted happen
        # when doing IMAGE_GENERATING after packages are generated.
        case = Case([[0, 0.2, 0.8, 0]])
        case.append_step(IMAGE_GENERATING)
        case.append_event(("BuildStarted", ))
        case.append_event(("sceneQueueTaskStarted", ))
        case.append_event(("runQueueTaskStarted", ))
        case.append_event(("BuildCompleted", ))
        self.view_build_progress.add_case(case)

        hbox.pack_start(self.view_build_progress, expand=True, fill=True)

        hbox_button = gtk.HBox(False, 0)
        hbox_button.set_border_width(1)
        hbox.pack_end(hbox_button, expand=False, fill=False)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.set_size_request(60, 35)
        hbox_button.pack_end(frame, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU)
        self.cancel = gtk.Button()
        self.cancel.set_image(image)
        self.cancel.connect("clicked", self.cancel_build_cb)
        frame.add(self.cancel)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.set_size_request(60, 35)
        hbox_button.pack_end(frame, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.detail = gtk.Button()
        self.detail.set_image(image)
        self.detail.connect("clicked", self.build_detail_cb)
        frame.add(self.detail)

        return hbox

    def create_image_address(self):
        hbox = gtk.HBox(False, 0)

        label = gtk.Label()
        label.set_markup("<span weight=\"bold\">Congratulations!</span> Find your image at:\n" + self.image_addr)
        hbox.pack_start(label, expand=False, fill=False, padding= 10)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.set_size_request(60, 35)
        hbox.pack_end(frame, expand=False, fill=False)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
        self.save = gtk.Button()
        self.save.set_image(image)
        self.save.connect("clicked", self.recipe_save_clicked_cb)
        frame.add(self.save)

        return hbox
 
    def need_reparse_cb(self, setting):
        if self.curr_mach:
            self.set_user_config()
            self.handler.generate_recipes()
            self.switch_page(RECIPE_GENERATING)

    def recipe_ready_cb(self, model):
        self.update_image_model()
        self.switch_page(RECIPE_GENERATED)

    def package_ready_cb(self, model):
        if self.current_step == PACKAGE_GENERATING:
            self.switch_page(PACKAGE_GENERATED)

    def recipe_reset_cb(self, selection):
        self.image_combo.set_active(0)

    def scroll_tv_cb(self, model, path, it, view):
        view.scroll_to_cell(path)

    def build_detail_cb(self, button):
        window = gtk.Dialog("Build Logs", None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        
        window.set_size_request(650, 600)

        build_tv = RunningBuildTreeView(readonly=True)
        build_tv.show()
        build_tv.set_model(self.build.model)
        self.build.model.connect("row-inserted", self.scroll_tv_cb, build_tv)
        scrolled_view = gtk.ScrolledWindow ()
        scrolled_view.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_view.add(build_tv)
        scrolled_view.show()
        window.vbox.pack_start(self.view_build_progress, expand=False, fill=False)
        window.vbox.pack_start(scrolled_view, expand=True, fill=True)
        hbox = gtk.HBox(False, 12)
        hbox.show()
        window.vbox.pack_start(hbox, expand=False, fill=False)

        response = window.run()
        window.destroy()

def main (server = None, eventHandler = None):
    params = {}
    # split_model indicates whether the Hob GUI and the bitbake server are
    # running on the same machine.
    split_model = False
    image_addr_prefix = ""
    if not eventHandler:
        helper = uihelper.BBUIHelper()
        server, eventHandler, server_addr, client_addr = helper.findServerDetails()
        image_addr_prefix = 'http://' + server_addr + ':'
        server.runCommand(["resetCooker"])
        if server_addr != client_addr:
            split_model = True

    gobject.threads_init()

    recipemodel = RecipeListModel()
    packagemodel = PackageListModel()
    handler = HobHandler(recipemodel, packagemodel, server)

    params["layer"] = server.runCommand(["getVariable", "BBLAYERS"]) or ""
    params["dldir"] = server.runCommand(["getVariable", "DL_DIR"]) or ""
    params["machine"] = server.runCommand(["getVariable", "MACHINE"]) or ""
    params["distro"] = server.runCommand(["getVariable", "DISTRO"]) or "defaultsetup"
    params["pclass"] = server.runCommand(["getVariable", "PACKAGE_CLASSES"]) or ""
    params["sstatedir"] = server.runCommand(["getVariable", "SSTATE_DIR"]) or ""
    params["sstatemirror"] = server.runCommand(["getVariable", "SSTATE_MIRROR"]) or ""

    num_threads = server.runCommand(["getDefaultNumOfThreads"])
    if not num_threads:
        num_threads = 1
    num_threads = int(num_threads)

    max_threads = server.runCommand(["getMaxNumOfThreads"])
    if not max_threads:
        max_threads = 1
    max_threads = int(max_threads)
    params["max_threads"] = max_threads

    bbthread = server.runCommand(["getVariable", "BB_NUMBER_THREADS"])
    if not bbthread:
        bbthread = num_threads
    else:
        bbthread = int(bbthread)
        if bbthread > max_threads:
            bbthread = max_threads
    params["bbthread"] = bbthread

    pmake = server.runCommand(["getVariable", "PARALLEL_MAKE"])
    if not pmake:
        pmake = num_threads
    else:
        pmake = int(pmake.lstrip("-j "))
        if pmake > max_threads:
            pmake = max_threads
    params["pmake"] = pmake

    image_addr = server.runCommand(["getVariable", "DEPLOY_DIR_IMAGE"]) or ""
    if image_addr_prefix:
        image_addr = image_addr_prefix + image_addr
    params["image_addr"] = image_addr

    image_extra_size = server.runCommand(["getVariable", "IMAGE_ROOTFS_EXTRA_SPACE"])
    if not image_extra_size:
        image_extra_size = 0
    else:
        image_extra_size = int(image_extra_size)
    params["image_extra_size"] = image_extra_size

    params["incompat_license"] = server.runCommand(["getVariable", "INCOMPATIBLE_LICENSE"]) or ""
    params["sdk_machine"] = server.runCommand(["getVariable", "SDKMACHINE"]) or server.runCommand(["getVariable", "SDK_ARCH"]) or ""

    try:
        # kick the while thing off
        if split_model:
            handler.commands_async.append(handler.CFG_AVAIL_LAYERS)
        else:
            handler.commands_async.append(handler.CFG_PATH_LAYERS)
        handler.commands_async.append(handler.CFG_FILES_DISTRO)
        handler.commands_async.append(handler.CFG_FILES_MACH)
        handler.commands_async.append(handler.CFG_FILES_SDKMACH)
        handler.commands_async.append(handler.FILES_MATCH_CLASS)
        handler.run_next_command()
    except xmlrpclib.Fault as x:
        print("XMLRPC Fault getting commandline:\n %s" % x)
        return 1

    window = MainWindow(split_model, recipemodel, packagemodel, handler, params)
    window.show_all ()

    handler.connect("machines-updated", window.update_machines)
    handler.connect("distros-updated", window.advanced_setting.update_distros)
    handler.connect("sdk-machines-updated", window.advanced_setting.update_sdk_machines)
    handler.connect("package-formats-found", window.advanced_setting.update_package_formats)
    handler.connect("layers-avail", window.layer_selection.load_avail_layers)
    handler.connect("generating-data", window.busy)
    handler.connect("data-generated", window.data_generated)
    handler.connect("command-succeeded", window.command_succeeded)
    handler.connect("command-failed", window.command_failed)
    

    # This timeout function regularly probes the event queue to find out if we
    # have any messages waiting for us.
    gobject.timeout_add (10,
                         handler.event_handle_idle_func,
                         eventHandler,
                         window)

    try:
        gtk.main()
    except EnvironmentError as ioerror:
        # ignore interrupted io
        if ioerror.args[0] == 4:
            pass
    finally:
        server.runCommand(["stateStop"])

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(5)
    sys.exit(ret)

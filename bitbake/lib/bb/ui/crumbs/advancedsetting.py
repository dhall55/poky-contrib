# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
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
import hashlib
from bb.ui.crumbs.hobwidget import HobWidget

VARIABLE_REPARSE = ["MULTILIBS", "MULTILIBS_append"]
class AdvancedSetting (gtk.Window):

    __gsignals__ = {
        "need-reparse"     : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                ()),
        }
    def __init__(self, split_model, params):
        gtk.Window.__init__(self)
        self.split_model = split_model
        self.curr_package_format = " ".join(params["pclass"].split("package_"))
        self.all_package_format = None
        self.curr_distro = params["distro"]
        self.all_distro = None
        self.curr_sdk_machine = params["sdk_machine"]
        self.all_sdk_machine = None
        self.dldir = params["dldir"]
        self.sstatedir = params["sstatedir"]
        self.sstatemirror = params["sstatemirror"]
        self.bbthread = params["bbthread"]
        self.pmake = params["pmake"]
        self.max_threads = params["max_threads"]
        self.image_extra_size = params["image_extra_size"]
        self.incompat_license = params["incompat_license"]
        self.toolchain_build = False
        self.extra_setting = {}
        self.pkgfmt_store = None
        self.distro_combo = None
        self.dldir_text = None
        self.sstatedir_text = None
        self.sstatemirror_text = None
        self.bb_spinner = None
        self.pmake_spinner = None
        self.extra_size_spinner = None
        self.gplv3_checkbox = None
        self.toolchain_checkbox = None
        self.setting_store = None

        self.variables = {}

    def update_package_formats(self, handler, formats):
        self.all_package_format = formats

    def update_distros(self, handler, distros):
        self.all_distro = distros

    def update_sdk_machines(self, handler, sdk_machines):
        self.all_sdk_machine = sdk_machines

    def main(self, button):
        window = gtk.Dialog("Advanced Settings", None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        
        window.set_size_request(450, 600)

        advanced_vbox = gtk.VBox(False, 15)
        advanced_vbox.set_border_width(20)
        
        advanced_viewport = gtk.Viewport()
        advanced_viewport.add(advanced_vbox)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add_with_viewport(advanced_viewport)
        window.vbox.pack_start(scroll, True, True, 5)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Packaging Format:</span>")
        tooltip = "Select package formats that will be used. The first format will be used for final image"
        pkgfmt_widget, self.pkgfmt_store = HobWidget.gen_pkgfmt_widget(self.curr_package_format, self.all_package_format, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(pkgfmt_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Select Distro:</span>")
        tooltip = "This is the Yocto distribution you would like to use"
        distro_widget, self.distro_combo = HobWidget.gen_combo_widget(self.curr_distro, self.all_distro, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(distro_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">BB_NUMBER_THREADS:</span>")
        tooltip = "Sets the number of threads that bitbake tasks can run simultaneously"
        bbthread_widget, self.bb_spinner = HobWidget.gen_spinner_widget(self.bbthread, 1, self.max_threads, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(bbthread_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">PARALLEL_MAKE:</span>")
        tooltip = "Sets the make parallism, as known as 'make -j'"
        pmake_widget, self.pmake_spinner = HobWidget.gen_spinner_widget(self.pmake, 1, self.max_threads, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(pmake_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Image Free Size: (MB)</span>")
        tooltip = "Sets the extra free space of your target image.\nDefaultly, system will reserve 30% of your image size as your free space. If your image contains zypper, it will bring in 50MB more space. The maximum free space is 1024MB."
        extra_size_widget, self.extra_size_spinner = HobWidget.gen_spinner_widget(int(self.image_extra_size*1.0/1024), 0, 1024, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(extra_size_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Set Download Directory:</span>")
        tooltip = "Select a folder that caches the upstream project source code"
        dldir_widget, self.dldir_text = HobWidget.gen_entry_widget(self.split_model, self.dldir, window, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(dldir_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Select SSTATE Directory:</span>")
        tooltip = "Select a folder that caches your prebuilt results"
        sstatedir_widget, self.sstatedir_text = HobWidget.gen_entry_widget(self.split_model, self.sstatedir, window, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(sstatedir_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Select SSTATE Mirror:</span>")
        tooltip = "Select the prebuilt mirror that will fasten your build speed"
        sstatemirror_widget, self.sstatemirror_text = HobWidget.gen_entry_widget(self.split_model, self.sstatemirror, window, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(sstatemirror_widget, expand=False, fill=False)

        self.gplv3_checkbox = gtk.CheckButton("Exclude GPLv3 packages")
        self.gplv3_checkbox.set_tooltip_text("Check this box to prevent GPLv3 packages from being included in your image")
        if "GPLv3" in self.incompat_license.split():
            self.gplv3_checkbox.set_active(True)
        else:
            self.gplv3_checkbox.set_active(False)
        advanced_vbox.pack_start(self.gplv3_checkbox)

        sub_hbox = gtk.HBox(False, 5)
        advanced_vbox.pack_start(sub_hbox, expand=False, fill=False)
        self.toolchain_checkbox = gtk.CheckButton("Build Toolchain")
        self.toolchain_checkbox.set_tooltip_text("Check this box to build the related toolchain with your image")
        self.toolchain_checkbox.set_active(self.toolchain_build)
        sub_hbox.pack_start(self.toolchain_checkbox, expand=False, fill=False)

        tooltip = "This is the Host platform you would like to run the toolchain"
        sdk_machine_widget, self.sdk_machine_combo = HobWidget.gen_combo_widget(self.curr_sdk_machine, self.all_sdk_machine, tooltip)
        sub_hbox.pack_start(sdk_machine_widget, expand=False, fill=False)

        sub_vbox = gtk.VBox(False, 5)
        advanced_vbox.pack_start(sub_vbox, expand=False, fill=False)
        label = HobWidget.gen_label_widget("<span weight=\"bold\">Add your own variables:</span>")
        tooltip = "This is the key/value pair for your extra settings"
        setting_widget, self.setting_store = HobWidget.gen_editable_settings(self.extra_setting, tooltip)
        sub_vbox.pack_start(label, expand=False, fill=False)
        sub_vbox.pack_start(setting_widget, expand=False, fill=False)

        hbox_button = gtk.HBox(False, 0)
        window.vbox.pack_end(hbox_button, expand=False, fill=False)
        button = gtk.Button("Cancel")
        button.connect("clicked", self.advanced_cancel_cb, window)
        hbox_button.pack_end(button, expand=False, fill=False)
        button = gtk.Button(" Save ")
        button.connect("clicked", self.advanced_ok_cb, window)
        hbox_button.pack_end(button, expand=False, fill=False)

        window.show_all()
        response = window.run()
        window.destroy()

    def advanced_ok_cb(self, button, window):
        self.curr_package_format = ""
        it = self.pkgfmt_store.get_iter_first()
        while it:
            value = self.pkgfmt_store.get_value(it, 2)
            if value:
                self.curr_package_format += (self.pkgfmt_store.get_value(it, 1) + " ")
            it = self.pkgfmt_store.iter_next(it)

        self.curr_distro = self.distro_combo.get_active_text()
        self.dldir = self.dldir_text.get_text()
        self.sstatedir = self.sstatedir_text.get_text()
        self.sstatemirror = self.sstatemirror_text.get_text()
        self.bbthread = self.bb_spinner.get_value_as_int()
        self.pmake = self.pmake_spinner.get_value_as_int()
        self.image_extra_size = self.extra_size_spinner.get_value_as_int() * 1024

        if self.gplv3_checkbox.get_active():
            if "GPLv3" not in self.incompat_license.split():
                self.incompat_license += " GPLv3"
        else:
            if "GPLv3" in self.incompat_license.split():
                self.incompat_license = self.incompat_license.split().remove("GPLv3")
                self.incompat_license = " ".join(self.incompat_license or [])

        self.toolchain_build = self.toolchain_checkbox.get_active()

        old_md5 = hashlib.md5(str(sorted(self.variables.items()))).hexdigest()
        self.variables = {}

        self.extra_setting = {}
        it = self.setting_store.get_iter_first()
        while it:
            key = self.setting_store.get_value(it, 0)
            value = self.setting_store.get_value(it, 1)
            self.extra_setting[key] = value
            if key in VARIABLE_REPARSE:
                self.variables[key] = value
            it = self.setting_store.iter_next(it)

        new_md5 = hashlib.md5(str(sorted(self.variables.items()))).hexdigest()
        if old_md5 != new_md5:
            self.emit("need-reparse")

        window.destroy()

    def advanced_cancel_cb(self, button, window):
        window.destroy()



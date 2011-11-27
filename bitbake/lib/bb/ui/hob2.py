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
from bb.ui.crumbs2.hobeventhandler import HobHandler
from bb.ui.crumbs2.hig import CrumbsDialog
import xmlrpclib
import logging
import Queue
import copy

class MainWindow (gtk.Window):

    def __init__(self,  handler, layers, mach, pclass, distro, bbthread, pmake, dldir, sstatedir, sstatemirror):
        gtk.Window.__init__(self)
        # global state
        self.layers = layers.split()
        self.layers_default = copy.copy(self.layers)
        self.curr_mach = mach
        self.machine_handler_id = None
        self.curr_distro = distro
        self.distro_handler_id = None
        self.curr_package_format = pclass
        self.package_handler_id = None
        self.bbthread = bbthread
        self.pmake = pmake
        self.dldir = dldir
        self.sstatedir = sstatedir
        self.sstatemirror = sstatemirror

        self.handler = handler

        self.connect("delete-event", self.destroy_window)
        self.set_title("HOB")
        self.set_icon_name("applications-development")
        self.set_default_size(1000, 650)

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(0)
        vbox.show()
        self.add(vbox)
        configview = self.create_config_gui()
        self.nb = gtk.Notebook()
        self.nb.append_page(configview)
        self.nb.set_current_page(0)
        self.nb.set_show_tabs(False)
        vbox.pack_start(self.nb, expand=True, fill=True)

    def load_current_layers(self, data):
        for layer in self.layers:
            self.layer_store.append([layer])

    def conf_error(self, lbl):
        dialog = CrumbsDialog(self, lbl)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        response = dialog.run()
        dialog.destroy()

    def add_layer_cb(self, action):
        dialog = gtk.FileChooserDialog("Add new layer", self,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        label = gtk.Label("Select the layer you wish to add")
        label.show()
        dialog.set_extra_widget(label)
        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()

        lbl = "<b>Error</b>\nUnable to load layer <i>%s</i> because " % path
        if response == gtk.RESPONSE_YES:
            # FIXME: verify we've actually got a layer conf?
            import os
            import os.path
            if not path:
                lbl += "it is an invalid path."
            elif not os.path.exists(path+"/conf/layer.conf"):
                lbl += "there is no layer.conf inside the directory."
            elif path in self.layers:
                lbl += "it is already in loaded layers."
            else:
                self.layer_store.append([path])
                self.layers.append(path)
                self.handler.layer_refresh(self.layers)
                return
            self.conf_error(lbl)

    def del_layer_cb(self, action):
        model, iter = self.ltv.get_selection().get_selected()
        lbl = "<b>Error</b>\nUnable to remove default layers <i>%s</i>" % self.layers_default
        if iter:
            layer = model.get_value(iter, 0)
            if layer in self.layers_default:
                self.conf_error(lbl)
            else:
                self.layer_store.remove(iter)
                self.layers.remove(layer)
                self.handler.layer_refresh(self.layers)

    def update_machines(self, handler, machines):
        active = 0
        # disconnect the signal handler before updating the combo model
        if self.machine_handler_id:
            self.machine_combo.disconnect(self.machine_handler_id)
            self.machine_handler_id = None

        model = self.machine_combo.get_model()
        if model:
            model.clear()

        for machine in machines:
            self.machine_combo.append_text(machine)
            if machine == self.curr_mach:
                self.machine_combo.set_active(active)
            active = active + 1

    def update_package_formats(self, handler, formats):
        active = 0
        # disconnect the signal handler before updating the model
        if self.package_handler_id:
            self.package_combo.disconnect(self.package_handler_id)
            self.package_handler_id = None

        model = self.package_combo.get_model()
        if model:
            model.clear()

        for format in formats:
            self.package_combo.append_text(format)
            if format == self.curr_package_format:
                self.package_combo.set_active(active)
            active = active + 1

    def update_distros(self, handler, distros):
        active = 0
        # disconnect the signal handler before updating combo model
        if self.distro_handler_id:
            self.distro_combo.disconnect(self.distro_handler_id)
            self.distro_handler_id = None

        model = self.distro_combo.get_model()
        if model:
            model.clear()

        for distro in distros:
            self.distro_combo.append_text(distro)
            if distro == self.curr_distro:
                self.distro_combo.set_active(active)
            active = active + 1

    def select_dldir_cb(self, action):
        dialog = gtk.FileChooserDialog("Select Download Directory", None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.dldir_text.set_text(path)

        dialog.destroy()

    def select_sstatedir_cb(self, action):
        dialog = gtk.FileChooserDialog("Select Sstate Directory", None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_YES,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_NO))
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            path = dialog.get_filename()
            self.sstatedir_text.set_text(path)

        dialog.destroy()

    def config_next_clicked_cb(self, button):
        self.handler.init_cooker()
        self.handler.set_bblayers(self.layers)
        self.handler.set_machine(self.machine_combo.get_active_text())
        self.handler.set_package_format(self.package_combo.get_active_text())
        self.handler.set_distro(self.distro_combo.get_active_text())
        self.handler.set_dl_dir(self.dldir_text.get_text())
        self.handler.set_sstate_dir(self.sstatedir_text.get_text())
        self.handler.set_sstate_mirror(self.sstatemirror_text.get_text())
        self.handler.set_pmake(self.pmake_spinner.get_value_as_int())
        self.handler.set_bbthreads(self.bb_spinner.get_value_as_int())

    def destroy_window(self, widget, event):
        gtk.main_quit()

    def create_config_gui(self):
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(5)
        vbox.show()

        table = gtk.Table(10, 5, False)
        table.show()
        vbox.pack_start(table, expand=False, fill=False)

        label = gtk.Label("Layers:")
        label.show()
        table.attach(label, 1, 2, 0, 2)

        self.layer_store = gtk.ListStore(gobject.TYPE_STRING)

        self.ltv = gtk.TreeView()
        self.ltv.set_model(self.layer_store)
        self.ltv.set_headers_visible(False)
        self.ltv.get_selection().set_mode(gtk.SELECTION_SINGLE)

        col0= gtk.TreeViewColumn('Path')
        self.ltv.append_column(col0)

        cell0 = gtk.CellRendererText()
        col0.pack_start(cell0, True)
        col0.set_attributes(cell0, text=0)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.ltv)

        table.attach(scroll, 2, 3, 0, 2)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_MENU)
        add_button = gtk.Button()
        add_button.set_image(image)
        add_button.connect("clicked", self.add_layer_cb)
        table.attach(add_button, 3, 4, 0, 1)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_MENU)
        del_button = gtk.Button()
        del_button.set_image(image)
        del_button.connect("clicked", self.del_layer_cb)
        table.attach(del_button, 3, 4, 1, 2)
        label = gtk.Label("Machine:")
        label.show()
        table.attach(label, 1, 2, 2, 3)

        self.machine_combo = gtk.combo_box_new_text()
        self.machine_combo.show()
        self.machine_combo.set_tooltip_text("Selects the architecture of the target board for which you would like to build an image.")
        table.attach(self.machine_combo, 2, 4, 2, 3)

        label = gtk.Label("Packaging:")
        label.show()
        table.attach(label, 1, 2, 3, 4)

        self.package_combo = gtk.combo_box_new_text()
        self.package_combo.show()
        table.attach(self.package_combo, 2, 4, 3, 4)

        label = gtk.Label("Distro:")
        label.show()
        table.attach(label, 1, 2, 4, 5)

        self.distro_combo = gtk.combo_box_new_text()
        self.distro_combo.set_tooltip_text("Select the Yocto distribution you would like to use")
        self.distro_combo.show()
        table.attach(self.distro_combo, 2, 4, 4, 5)

        label = gtk.Label("DL_DIR:")
        label.show()
        table.attach(label, 1, 2, 5, 6)

        self.dldir_text = gtk.Entry()
        self.dldir_text.set_text(self.dldir or "")
        self.dldir_text.show()
        table.attach(self.dldir_text, 2, 3, 5, 6)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_MENU)
        open_button = gtk.Button()
        open_button.set_image(image)
        open_button.connect("clicked", self.select_dldir_cb)
        table.attach(open_button, 3, 4, 5, 6)


        label = gtk.Label("SSTATE_DIR:")
        label.show()
        table.attach(label, 1, 2, 6, 7)

        self.sstatedir_text = gtk.Entry()
        self.sstatedir_text.set_text(self.sstatedir or "")
        self.sstatedir_text.show()
        table.attach(self.sstatedir_text, 2, 3, 6, 7)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_MENU)
        open_button = gtk.Button()
        open_button.set_image(image)
        open_button.connect("clicked", self.select_sstatedir_cb)
        table.attach(open_button, 3, 4, 6, 7)

        label = gtk.Label("SSTATE_MIRROR:")
        label.show()
        table.attach(label, 1, 2, 7, 8)

        self.sstatemirror_text = gtk.Entry()
        self.sstatemirror_text.set_text(self.sstatemirror or "")
        self.sstatemirror_text.show()
        table.attach(self.sstatemirror_text, 2, 4, 7, 8)

        label = gtk.Label("BB_NUMBER_THREADS:")
        label.show()
        table.attach(label, 1, 2, 8, 9)
        bb_adjust = gtk.Adjustment(value=self.bbthread, lower=1, upper=16, step_incr=1)
        self.bb_spinner = gtk.SpinButton(adjustment=bb_adjust, climb_rate=1, digits=0)
        self.bb_spinner.show()
        table.attach(self.bb_spinner, 2, 4, 8, 9)

        label = gtk.Label("PARALLEL_MAKE:")
        label.show()
        table.attach(label, 1, 2, 9, 10)

        pmake_adjust = gtk.Adjustment(value=self.pmake, lower=1, upper=16, step_incr=1)
        self.pmake_spinner = gtk.SpinButton(adjustment=pmake_adjust, climb_rate=1, digits=0)
        self.pmake_spinner.show()
        table.attach(self.pmake_spinner, 2, 4, 9, 10)

        bbox = gtk.HButtonBox()
        bbox.set_spacing(12)
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.show()
        vbox.pack_start(bbox, expand=False, fill=False)
        bake = gtk.Button("Next")
        bake.connect("clicked", self.config_next_clicked_cb)
        bake.show()
        bbox.add(bake)

        return vbox


def main (server, eventHandler):
    gobject.threads_init()

    handler = HobHandler(server)

    layers = server.runCommand(["getVariable", "BBLAYERS"])
    dldir = server.runCommand(["getVariable", "DL_DIR"])
    mach = server.runCommand(["getVariable", "MACHINE"])
    distro = server.runCommand(["getVariable", "DISTRO"]) or "defaultsetup"
    sstatedir = server.runCommand(["getVariable", "SSTATE_DIR"])
    sstatemirror = server.runCommand(["getVariable", "SSTATE_MIRROR"])

    pclasses = server.runCommand(["getVariable", "PACKAGE_CLASSES"]).split(" ")
    pkg, sep, pclass = pclasses[0].rpartition("_")

    bbthread = server.runCommand(["getVariable", "BB_NUMBER_THREADS"])
    if not bbthread:
        bbthread = 1
    else:
        bbthread = int(bbthread)

    pmake = server.runCommand(["getVariable", "PARALLEL_MAKE"])
    if not pmake:
        pmake = 1
    else:
        pmake = int(pmake.lstrip("-j "))

    try:
        # kick the while thing off
        handler.next_command = handler.CFG_PATH_LAYERS
        handler.run_next_command()
    except xmlrpclib.Fault:
        print("XMLRPC Fault getting commandline:\n %s" % x)
        return 1

    window = MainWindow(handler, layers, mach, pclass, distro, bbthread, pmake, dldir, sstatedir, sstatemirror)
    window.show_all ()
    handler.connect("machines-updated", window.update_machines)
    handler.connect("distros-updated", window.update_distros)
    handler.connect("package-formats-found", window.update_package_formats)
    handler.connect("layers-found", window.load_current_layers)

    # This timeout function regularly probes the event queue to find out if we
    # have any messages waiting for us.
    gobject.timeout_add (100,
                         handler.event_handle_idle_func,
                         eventHandler)

    try:
        gtk.main()
    except EnvironmentError as ioerror:
        # ignore interrupted io
        if ioerror.args[0] == 4:
            pass
    finally:
        server.runCommand(["stateStop"])

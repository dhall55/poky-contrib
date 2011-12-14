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

import gobject
import logging
import tempfile
import datetime

progress_total = 0

class HobHandler(gobject.GObject):

    """
    This object does BitBake event handling for the hob gui.
    """
    __gsignals__ = {
         "layers-found"       : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE,
                                 ()),
         "package-formats-found" : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "machines-updated"    : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "distros-updated"     : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_PYOBJECT,)),
         "command-failed"      : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  (gobject.TYPE_STRING,)),
         "generating-data"     : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  ()),
         "data-generated"      : (gobject.SIGNAL_RUN_LAST,
                                  gobject.TYPE_NONE,
                                  ()),
    }

    (CFG_PATH_LAYERS, CFG_FILES_DISTRO, CFG_FILES_MACH, FILES_MATCH_CLASS, PARSE_CONFIG, GENERATE_TGTS, BUILD_RECIPES, CMD_END) = range(8)

    def __init__(self, recipemodel, server):
        gobject.GObject.__init__(self)

        self.next_command = None
        self.generating = False
        self.current_phase = None
        self.building = False

        self.recipe_model = recipemodel
        self.server = server

    def set_busy(self):
        if self.next_command and not self.generating:
            self.emit("generating-data")
            self.generating = True

    def clear_busy(self):
        if self.generating:
            self.emit("data-generated")
            self.generating = False

    def run_next_command(self):
        self.set_busy()
        if self.next_command == self.CFG_PATH_LAYERS:
            self.next_command = self.CFG_FILES_DISTRO
            ret = self.server.runCommand(["findConfigFilePath", "bblayers.conf"])
        elif self.next_command == self.CFG_FILES_DISTRO:
            self.next_command = self.CFG_FILES_MACH
            ret = self.server.runCommand(["findConfigFiles", "DISTRO"])
        elif self.next_command == self.CFG_FILES_MACH:
            self.next_command = self.FILES_MATCH_CLASS
            ret = self.server.runCommand(["findConfigFiles", "MACHINE"])
        elif self.next_command == self.FILES_MATCH_CLASS:
            self.next_command = self.CMD_END
            ret = self.server.runCommand(["findFilesMatchingInDir", "rootfs_", "classes"])

        elif self.next_command == self.PARSE_CONFIG:
            self.next_command = self.GENERATE_TGTS
            self.server.runCommand(["parseConfigurationFiles", "", ""])
        elif self.next_command == self.GENERATE_TGTS:
            self.next_command = self.CMD_END
            self.server.runCommand(["generateTargetsTree", "classes/image.bbclass", [], True])

        elif self.next_command == self.BUILD_RECIPES:
            self.clear_busy()
            self.building = True
            self.server.runCommand(["buildTargets", self.build_queue, "build"])
            self.build_queue = []
            self.next_command = None

        elif self.next_command == self.CMD_END:
            self.clear_busy()
            self.next_command = None
                                                                         
    def handle_event(self, event, window):
        if not event:
            return

        if self.building:
            self.current_phase = "building"
            window.build.handle_event(event, window.view_build_progress)
        elif isinstance(event, bb.event.TargetsTreeGenerated):
            self.current_phase = "data generation"
            if event._model:
                self.recipe_model.populate(event._model)
        elif isinstance(event, bb.event.ConfigFilesFound):
            self.current_phase = "configuration lookup"
            var = event._variable
            if var == "distro":
            	distros = event._values
            	distros.sort()
            	self.emit("distros-updated", distros)
            elif var == "machine":
                machines = event._values
            	machines.sort()
            	self.emit("machines-updated", machines)
        elif isinstance(event, bb.event.ConfigFilePathFound):
            self.current_phase = "configuration lookup"
            self.emit("layers-found")
        elif isinstance(event, bb.event.FilesMatchingFound):
            self.current_phase = "configuration lookup"
            # FIXME: hard coding, should at least be a variable shared between
            # here and the caller
            if event._pattern == "rootfs_":
                formats = []
                for match in event._matches:
                    classname, sep, cls = match.rpartition(".")
                    fs, sep, format = classname.rpartition("_")
                    formats.append(format)
                formats.sort()
                self.emit("package-formats-found", formats)
        elif isinstance(event, bb.command.CommandCompleted):
            self.current_phase = None
            self.run_next_command()
        elif isinstance(event, bb.command.CommandFailed):
            self.emit("command-failed", event.error)
        elif isinstance(event, bb.event.OperationStarted) and window and window.create_recipe_progress:
            window.create_recipe_progress.update(0)
            window.create_recipe_progress.set_title(event.msg)
        elif isinstance(event, bb.event.OperationProgress) and window and window.create_recipe_progress:
            window.create_recipe_progress.update(event.current, event.total)
            window.create_recipe_progress.set_title(event.msg)
        elif isinstance(event, bb.event.OperationCompleted) and window and window.create_recipe_progress:
            window.create_recipe_progress.update(event.total, event.total)
            window.create_recipe_progress.set_title(event.msg)
        return

    def event_handle_idle_func (self, eventHandler, window):
        # Consume as many messages as we can in the time available to us
        event = eventHandler.getEvent()
        while event:
            self.handle_event(event, window)
            event = eventHandler.getEvent()
        return True

    def init_cooker(self):
        self.server.runCommand(["initCooker"])

    def layer_refresh(self, bblayers):
        self.server.runCommand(["initCooker"])
        self.server.runCommand(["initParser"])
        self.server.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])
        self.server.runCommand(["parseConfigurationFiles", "", ""])
        self.next_command = self.CFG_FILES_DISTRO
        self.run_next_command()

    def set_bblayers(self, bblayers):
        self.server.runCommand(["setVariable", "BBLAYERS", " ".join(bblayers)])

    def set_machine(self, machine):
        self.server.runCommand(["setVariable", "MACHINE", machine])

    def set_distro(self, distro):
        self.server.runCommand(["setVariable", "DISTRO", distro])

    def set_package_format(self, format):
        self.server.runCommand(["setVariable", "PACKAGE_CLASSES", "package_%s" % format])

    def set_bbthreads(self, threads):
        self.server.runCommand(["setVariable", "BB_NUMBER_THREADS", threads])

    def set_pmake(self, threads):
        pmake = "-j %s" % threads
        self.server.runCommand(["setVariable", "PARALLEL_MAKE", pmake])

    def set_dl_dir(self, directory):
        self.server.runCommand(["setVariable", "DL_DIR", directory])

    def set_sstate_dir(self, directory):
        self.server.runCommand(["setVariable", "SSTATE_DIR", directory])

    def set_sstate_mirror(self, url):
        self.server.runCommand(["setVariable", "SSTATE_MIRROR", url])

    def generate_data(self, config=None):
        self.next_command = self.PARSE_CONFIG
        self.run_next_command()
                 
    def build_targets(self, tgts):
        targets = []
        targets.extend(tgts)
        self.build_queue = targets
        self.next_command = self.BUILD_RECIPES
        self.run_next_command()

    def cancel_build(self, force=False):
        if force:
            # Force the cooker to stop as quickly as possible
            self.server.runCommand(["stateStop"])
        else:
            # Wait for tasks to complete before shutting down, this helps
            # leave the workdir in a usable state
            self.server.runCommand(["stateShutdown"])



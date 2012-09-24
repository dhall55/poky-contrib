#!/usr/bin/env python
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Lv Xiaotong <xiaotongx.lv@intel.com>
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

import logging

class WSEventHandler:
    def __init__ (self):
        self.ret_value = {}

    def clear_ret_value(self):
        if self.ret_value:
            self.ret_value = {}

    #To convert the list type in recipe and packages tree model into string type.
    #so that the tree model can be converted into standard json data
    def treemodel_list_tostring(self, data):
        for k, v in data.iteritems():
            if isinstance(v, dict):
                data[k] = self.treemodel_list_tostring(v)
            elif isinstance(v, list):
                data[k] = 'list:'+' '.join(v)
            else:
                data[k] = v
        return data

    def handle_event(self, event):
        
        if not event:
            return

        self.clear_ret_value()

        if isinstance(event, bb.event.PackageInfo):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["pkginfolist"] = event._pkginfolist
        elif isinstance(event, bb.event.SanityCheckPassed):
            self.ret_value["event"] = bb.event.getName(event)
        elif isinstance(event, bb.event.SanityCheckFailed):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["msg"] = event._msg
        elif isinstance(event, bb.event.SanityCheck):
            self.ret_value["event"] = bb.event.getName(event)
        elif isinstance(event, logging.LogRecord):
                self.ret_value["event"] = bb.event.getName(event)
                self.ret_value["msg"] = event.msg
                self.ret_value["getMessage"] = event.getMessage()
                self.ret_value["logging_ERROR"] = logging.ERROR
                self.ret_value["logging_WARNING"] = logging.WARNING
                self.ret_value["levelno"] = event.levelno

        elif isinstance(event, bb.event.TargetsTreeGenerated):
            self.ret_value["event"] = bb.event.getName(event)
            if event._model:
                self.ret_value["model"] = self.treemodel_list_tostring(event._model)

        elif isinstance(event, bb.event.ConfigFilesFound):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["variable"] = event._variable
            self.ret_value["values"] = ' '.join(event._values)

        elif isinstance(event, bb.event.ConfigFilePathFound):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["path"] = event._path

        elif isinstance(event, bb.event.FilesMatchingFound):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["pattern"] = event._pattern
            self.ret_value["matches"] = ' '.join(event._matches)

        elif isinstance(event, bb.command.CommandCompleted):
            self.ret_value["event"] = bb.event.getName(event)

        elif isinstance(event, bb.command.CommandFailed):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["exitcode"] = event.exitcode
            self.ret_value["error"] = event.error

        elif isinstance(event, (bb.event.ParseStarted,
                                bb.event.CacheLoadStarted,
                                bb.event.TreeDataPreparationStarted)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            if self.ret_value["event"] != 'TreeDataPreparationStarted':
                self.ret_value["total"] = event.total

        elif isinstance(event, (bb.event.ParseProgress,
                                bb.event.CacheLoadProgress,
                                bb.event.TreeDataPreparationProgress)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["current"] = event.current
            self.ret_value["total"] = event.total
            self.ret_value["msg"] = event.msg

        elif isinstance(event, (bb.event.ParseCompleted,
                                bb.event.CacheLoadCompleted,
                                bb.event.TreeDataPreparationCompleted)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["total"] = event.total
            self.ret_value["msg"] = event.msg

        elif isinstance(event, bb.event.NoProvider):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["dependees"] = ' '.join(event._dependees)
            self.ret_value["reasons"] = ' '.join(event._reasons)
            self.ret_value["runtime"] = event._runtime
            self.ret_value["item"] = event._item

        elif isinstance(event, bb.event.MultipleProviders):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["candidates"] = ' '.join(event._candidates)
            self.ret_value["runtime"] = event._runtime
            self.ret_value["item"] = event._item

        elif isinstance(event, bb.event.BuildStarted):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["name"] = event._name
            self.ret_value["msg"] = event.msg
            self.ret_value["failures"] = event._failures
            self.ret_value["pkgs"] = ' '.join(event._pkgs)
            self.ret_value["pid"] = event.pid

        elif isinstance(event, bb.event.BuildCompleted):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["name"] = event._name
            self.ret_value["msg"] = event.msg
            self.ret_value["failures"] = event._failures
            self.ret_value["total"] = event.total
            self.ret_value["pkgs"] = ' '.join(event._pkgs)
            self.ret_value["pid"] = event.pid

        elif isinstance(event, (bb.build.TaskBase,
                                bb.build.TaskStarted,
                                bb.build.TaskSucceeded)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["task"] = event._task
            self.ret_value["message"] = event._message
            self.ret_value["package"] = event._package
            self.ret_value["pid"] = event.pid

        if isinstance(event, bb.build.TaskFailed):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["logfile"] = event.logfile
            self.ret_value["errprinted"] = event.errprinted

        elif isinstance(event, (bb.runqueue.runQueueTaskStarted,
                                bb.runqueue.sceneQueueTaskStarted)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["noexec"] = event.noexec
            self.ret_value["taskstring"] = event.taskstring
            self.ret_value["taskid"] = event.taskid
            self.ret_value["stats"] = {'completed':event.stats.completed,
                                       'active':event.stats.active,
                                       'failed':event.stats.failed,
                                       'total':event.stats.total
                                       }
            self.ret_value["pid"] = event.pid

        elif isinstance(event, bb.runqueue.runQueueTaskCompleted):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["taskstring"] = event.taskstring
            self.ret_value["pid"] = event.pid
            self.ret_value["taskid"] = event.taskid

        elif isinstance(event, (bb.runqueue.runQueueTaskFailed,
                                bb.runqueue.sceneQueueTaskFailed)
                        ):
            self.ret_value["event"] = bb.event.getName(event)
            self.ret_value["taskid"] = event.taskid
            self.ret_value["exitcode"] = event.exitcode
            self.ret_value["taskstring"] = event.taskstring
            self.ret_value["pid"] = event.pid

        return self.ret_value

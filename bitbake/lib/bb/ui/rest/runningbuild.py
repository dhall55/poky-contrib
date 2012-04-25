#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2008        Intel Corporation
#
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
import time
import urllib
import urllib2

class RunningBuild:
    def __init__ (self):
        self.event_result = None

    def handle_event (self, event):
        if self.event_result:
            self.event_result = None

        if(isinstance(event, logging.LogRecord)):
            if event.msg.startswith("Execution of event handler 'run_buildstats' failed"):
                return

            if (event.levelno < logging.INFO or
                event.msg.startswith("Running task")):
                return # don't add these to the list

            if event.levelno >= logging.ERROR:
                self.event_result  = {'event': bb.event.getName(event),
                                      'value': event.getMessage(),
                             }
            elif event.levelno >= logging.WARNING:
                self.event_result  = {'event': bb.event.getName(event),
                                      'value': event.getMessage(),
                             }
            else:
                self.event_result  = {'event': bb.event.getName(event),
                                      'value': event.getMessage(),
                             }
        elif isinstance(event, bb.build.TaskStarted):
            (package, task) = (event._package, event._task)
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': {'package':package,
                                            'task':task,
                                            }
                                  }
        elif isinstance(event, bb.build.TaskBase):
            if isinstance(event, bb.build.TaskFailed):
                logfile = event.logfile
                if logfile and os.path.exists(logfile):
                    with open(logfile) as f:
                        logdata = f.read()
                        self.event_result  = {'event': bb.event.getName(event),
                                              'value': {'logdata':logdata}
                                        }
        elif isinstance(event, bb.event.BuildStarted):
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': "Build Started (%s)" % time.strftime('%m/%d/%Y %H:%M:%S')
                                 }
        elif isinstance(event, bb.command.CommandFailed):
            if event.error.startswith("Exited with"):
                self.event_result  = {'event': bb.event.getName(event),
                                      'value': {'error':event.error}
                                }
        elif isinstance(event, bb.event.CacheLoadStarted):
            self.progress_total = event.total
            self.event_result  = {'event': bb.event.getName(event),
                             'value': {'progress_total':self.progress_total}}
        elif isinstance(event, bb.event.CacheLoadProgress):
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': {'current':event.current,
                                            'progress_total':self.progress_total
                                           }
                                 }
        elif isinstance(event, bb.event.CacheLoadCompleted):
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': {'progress_total':self.progress_total}}
        elif isinstance(event, bb.event.ParseStarted):
            self.progress_total = event.total
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': {'progress_total':event.total}}
        elif isinstance(event, bb.event.ParseProgress):
            pbar.update(event.current, self.progress_total)
        elif isinstance(event, bb.event.ParseCompleted):
            pass
#            self.event_result  = {'event': bb.event.getName(event),
#                                  'value': '~ParseCompleted~'}
        elif isinstance(event, (bb.runqueue.runQueueTaskStarted,
                                bb.runqueue.sceneQueueTaskStarted)):
            num_of_completed = event.stats.completed + event.stats.failed
            self.event_result  = {'event': bb.event.getName(event),
                                  'value': {'num_of_completed': num_of_completed,
                                            'total':event.stats.total
                                           }
                                 }
        return self.event_result
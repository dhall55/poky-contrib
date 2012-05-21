# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake Smart Dictionary Implementation

Functions for interacting with the data structure used by the
BitBake build tools.

"""

# Copyright (C) 2003, 2004  Chris Larson
# Copyright (C) 2004, 2005  Seb Frankengul
# Copyright (C) 2005, 2006  Holger Hans Peter Freyther
# Copyright (C) 2005        Uli Luckas
# Copyright (C) 2005        ROAD GmbH
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
# Based on functions from the base bb module, Copyright 2003 Holger Schurig

import traceback
import copy, re
import sys
from collections import MutableMapping
import logging
import hashlib
import bb, bb.codeparser
from bb   import utils
from bb.COW  import COWDictBase

logger = logging.getLogger("BitBake.Data")

__setvar_keyword__ = ["_append", "_prepend"]
__setvar_regexp__ = re.compile('(?P<base>.*?)(?P<keyword>_append|_prepend)(_(?P<add>.*))?$')
__expand_var_regexp__ = re.compile(r"\${[^{}]+}")
__expand_python_regexp__ = re.compile(r"\${@.+?}")


class VariableParse:
    def __init__(self, varname, d, val = None):
        self.varname = varname
        self.d = d
        self.value = val

        self.references = set()
        self.execs = set()

    def var_sub(self, match):
            key = match.group()[2:-1]
            if self.varname and key:
                if self.varname == key:
                    raise Exception("variable %s references itself!" % self.varname)
            var = self.d.getVar(key, True)
            if var is not None:
                self.references.add(key)
                return var
            else:
                return match.group()

    def python_sub(self, match):
            code = match.group()[3:-1]
            codeobj = compile(code.strip(), self.varname or "<expansion>", "eval")

            parser = bb.codeparser.PythonParser(self.varname, logger)
            parser.parse_python(code)
            if self.varname:
                vardeps = self.d.getVarFlag(self.varname, "vardeps", True)
                if vardeps is None:
                    parser.log.flush()
            else:
                parser.log.flush()
            self.references |= parser.references
            self.execs |= parser.execs

            value = utils.better_eval(codeobj, DataContext(self.d))
            return str(value)


class DataContext(dict):
    def __init__(self, metadata, **kwargs):
        self.metadata = metadata
        dict.__init__(self, **kwargs)
        self['d'] = metadata

    def __missing__(self, key):
        value = self.metadata.getVar(key, True)
        if value is None or self.metadata.getVarFlag(key, 'func'):
            raise KeyError(key)
        else:
            return value

class ExpansionError(Exception):
    def __init__(self, varname, expression, exception):
        self.expression = expression
        self.variablename = varname
        self.exception = exception
        if varname:
            self.msg = "Failure expanding variable %s, expression was %s which triggered exception %s: %s" % (varname, expression, type(exception).__name__, exception)
        else:
            self.msg = "Failure expanding expression %s which triggered exception %s: %s" % (expression, type(exception).__name__, exception)
        Exception.__init__(self, self.msg)
        self.args = (varname, expression, exception)
    def __str__(self):
        return self.msg

class DataSmart(MutableMapping):
    def __init__(self, special = COWDictBase.copy(), seen = COWDictBase.copy() ):
        self.dict = {}
        self.history = {}
        self.include_history = []
        self.include_stack = [(-1, self.include_history)]

        # cookie monster tribute
        self._special_values = special
        self._seen_overrides = seen
        self._tracking_enabled = False

        self.expand_cache = {}

    def includeLog(self, filename):
        """includeLog(included_file) shows that the file was included
        by the currently-processed file or context."""
        if self._tracking_enabled:
            event = (filename, [])
            position = (len(self.include_stack[-1][1]), event[1])
            self.include_stack[-1][1].append(event)
            self.include_stack.append(position)

    def includeLogDone(self, filename):
        if self._tracking_enabled:
            if len(self.include_stack) > 1:
                self.include_stack.pop()
            else:
                bb.warn("Uh-oh:  includeLogDone(%s) tried to empty the stack." % filename)

    def getIncludeHistory(self):
        return self.include_history

    def tracking(self):
        return self._tracking_enabled

    def enableTracking(self):
        self._tracking_enabled = True

    def disableTracking(self):
        self._tracking_enabled = False

    def eventLog(self, var, event, value, filename = None, lineno = None):
        if self._tracking_enabled and filename != 'Ignore':
            if var not in self.history:
                self.history[var] = []
            self.history[var].append((event, filename, lineno, value))

    def expandWithRefs(self, s, varname):

        if not isinstance(s, basestring): # sanity check
            return VariableParse(varname, self, s)

        if varname and varname in self.expand_cache:
            return self.expand_cache[varname]

        varparse = VariableParse(varname, self)

        while s.find('${') != -1:
            olds = s
            try:
                s = __expand_var_regexp__.sub(varparse.var_sub, s)
                s = __expand_python_regexp__.sub(varparse.python_sub, s)
                if s == olds:
                    break
            except ExpansionError:
                raise
            except Exception as exc:
                raise ExpansionError(varname, s, exc)

        varparse.value = s

        if varname:
            self.expand_cache[varname] = varparse

        return varparse

    def expand(self, s, varname = None):
        return self.expandWithRefs(s, varname).value

    # Figure out how to describe the caller when file/line weren't
    # specified.
    def infer_file_and_line(self, filename, lineno):
        details = lineno
        if self._tracking_enabled and not filename and filename != 'Ignore':
            filename, lineno, func, line = traceback.extract_stack(limit=3)[0]
            details = "%d [%s]" % (lineno, func)
        return filename, details

    def finalize(self):
        """Performs final steps upon the datastore, including application of overrides"""

        overrides = (self.getVar("OVERRIDES", True) or "").split(":") or []

        #
        # Well let us see what breaks here. We used to iterate
        # over each variable and apply the override and then
        # do the line expanding.
        # If we have bad luck - which we will have - the keys
        # where in some order that is so important for this
        # method which we don't have anymore.
        # Anyway we will fix that and write test cases this
        # time.

        #
        # First we apply all overrides
        # Then  we will handle _append and _prepend
        #

        for o in overrides:
            # calculate '_'+override
            l = len(o) + 1

            # see if one should even try
            if o not in self._seen_overrides:
                continue

            vars = self._seen_overrides[o].copy()
            for var in vars:
                name = var[:-l]
                try:
                    # Move the history of the override into the history of
                    # the overridden:
                    for event in self.getHistory(var):
                        self.eventLog(name, 'override:%s' % o, event[3], event[1], event[2])
                    self.setVar(name, self.getVar(var, False), 'Ignore')
                    self.delVar(var, 'Ignore')
                except Exception, e:
                    logger.info("Untracked delVar %s: %s" % (var, e))

        # now on to the appends and prepends
        for op in __setvar_keyword__:
            if op in self._special_values:
                appends = self._special_values[op] or []
                for append in appends:
                    keep = []
                    for (a, o) in self.getVarFlag(append, op) or []:
                        match = True
                        if o:
                            for o2 in o.split("_"):
                                if not o2 in overrides:
                                    match = False
                        if not match:
                            keep.append((a ,o))
                            continue

                        if op == "_append":
                            sval = self.getVar(append, False) or ""
                            sval += a
                            self.setVar(append, sval, 'Ignore')
                        elif op == "_prepend":
                            sval = a + (self.getVar(append, False) or "")
                            self.setVar(append, sval, 'Ignore')

                    # We save overrides that may be applied at some later stage
                    # ... but we don't need to report on this.
                    if keep:
                        self.setVarFlag(append, op, keep, 'Ignore')
                    else:
                        self.delVarFlag(append, op, 'Ignore')

    def initVar(self, var):
        self.expand_cache = {}
        if not var in self.dict:
            self.dict[var] = {}

    def _findVar(self, var):
        dest = self.dict
        while dest:
            if var in dest:
                return dest[var]

            if "_data" not in dest:
                break
            dest = dest["_data"]

    def _makeShadowCopy(self, var):
        if var in self.dict:
            return

        local_var = self._findVar(var)

        if local_var:
            self.dict[var] = copy.copy(local_var)
        else:
            self.initVar(var)

    # In some cases, we want to set a value, but only record part of it;
    # for instance, when appending something, we want to record what we
    # appended, not what the complete value of the now-appended value.
    # This becomes especially obvious when looking at the output for
    # BBCLASSEXTEND. "details", if provided, replace the variable value
    # in the log.

    def setVar(self, var, value, filename = None, lineno = None, op = 'set', details = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        self.expand_cache = {}
        match  = __setvar_regexp__.match(var)
        if match and match.group("keyword") in __setvar_keyword__:
            base = match.group('base')
            keyword = match.group("keyword")
            override = match.group('add')
            l = self.getVarFlag(base, keyword) or []
            # Compute new details: This is what we're actually appending.
            details = [value, override]
            l.append(details)
            # Log the details using the keyword as the op name, instead
            # of logging the entire new value as a flag change.
            self.setVarFlag(base, keyword, l, 'Ignore')
            self.eventLog(base, keyword, details, filename, lineno)

            # todo make sure keyword is not __doc__ or __module__
            # pay the cookie monster
            try:
                self._special_values[keyword].add( base )
            except KeyError:
                self._special_values[keyword] = set()
                self._special_values[keyword].add( base )

            return

        if not var in self.dict:
            self._makeShadowCopy(var)

        # more cookies for the cookie monster
        if '_' in var:
            override = var[var.rfind('_')+1:]
            if len(override) > 0:
                if override not in self._seen_overrides:
                    self._seen_overrides[override] = set()
                self._seen_overrides[override].add( var )

        # setting var
        self.dict[var]["content"] = value
        self.eventLog(var, op, details or value, filename, lineno)

    def getHistory(self, var):
        if var in self.history:
            return self.history[var]
        return []

    def getVar(self, var, expand=False, noweakdefault=False):
        value = self.getVarFlag(var, "content", False, noweakdefault)

        # Call expand() separately to make use of the expand cache
        if expand and value:
            return self.expand(value, var)
        return value

    def renameVar(self, key, newkey, filename = None, lineno = None):
        """
        Rename the variable key to newkey
        """
        filename, lineno = self.infer_file_and_line(filename, lineno)
        val = self.getVar(key, 0)
        if val is not None:
            self.setVar(newkey, val, filename, lineno, 'rename-create')

        for i in ('_append', '_prepend'):
            src = self.getVarFlag(key, i)
            if src is None:
                continue

            dest = self.getVarFlag(newkey, i) or []
            dest.extend(src)
            self.setVarFlag(newkey, i, dest, filename, lineno, 'rename')

            if i in self._special_values and key in self._special_values[i]:
                self._special_values[i].remove(key)
                self._special_values[i].add(newkey)

        self.delVar(key, filename, lineno, 'rename-delete')

    def appendVar(self, key, newValue, filename = None, lineno = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        value = (self.getVar(key, False) or "") + newValue
        self.setVar(key, value, filename, lineno, 'append', newValue)

    def prependVar(self, key, newValue, filename = None, lineno = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        value = newValue + (self.getVar(key, False) or "")
        self.setVar(key, value, filename, lineno, 'prepend', newValue)

    def delVar(self, var, filename = None, lineno = None, op = 'del'):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        self.expand_cache = {}
        self.dict[var] = {}
        self.eventLog(var, op, '', filename, lineno)
        if '_' in var:
            override = var[var.rfind('_')+1:]
            if override and override in self._seen_overrides and var in self._seen_overrides[override]:
                self._seen_overrides[override].remove(var)

    def setVarFlag(self, var, flag, flagvalue, filename = None, lineno = None, op = 'set', details = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        if not var in self.dict:
            self._makeShadowCopy(var)
        self.dict[var][flag] = flagvalue
        self.eventLog(var, '[flag %s] %s' % (flag, op), details or flagvalue, filename, lineno)

    def getVarFlag(self, var, flag, expand=False, noweakdefault=False):
        local_var = self._findVar(var)
        value = None
        if local_var:
            if flag in local_var:
                value = copy.copy(local_var[flag])
            elif flag == "content" and "defaultval" in local_var and not noweakdefault:
                value = copy.copy(local_var["defaultval"])
        if expand and value:
            value = self.expand(value, None)
        return value

    def delVarFlag(self, var, flag, filename = None, lineno = None):
        local_var = self._findVar(var)
        if not local_var:
            return
        if not var in self.dict:
            self._makeShadowCopy(var)

        filename, lineno = self.infer_file_and_line(filename, lineno)
        self.eventLog(var, 'del flag %s' % flag, '', filename, lineno)
        if var in self.dict and flag in self.dict[var]:
            del self.dict[var][flag]

    def appendVarFlag(self, key, flag, newValue, filename = None, lineno = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        value = (self.getVarFlag(key, flag, False) or "") + newValue
        self.setVarFlag(key, flag, value, filename, lineno, 'append', newValue)

    def prependVarFlag(self, key, flag, newValue, filename = None, lineno = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        value = newValue + (self.getVarFlag(key, flag, False) or "")
        self.setVarFlag(key, flag, value, filename, lineno, 'prepend', newValue)

    def setVarFlags(self, var, flags, filename = None, lineno = None, details = None):
        filename, lineno = self.infer_file_and_line(filename, lineno)
        if not var in self.dict:
            self._makeShadowCopy(var)

        for i in flags:
            if i == "content":
                continue
            self.eventLog(var, 'set flag %s' % i, details or flags[i], filename, lineno)
            self.dict[var][i] = flags[i]

    def getVarFlags(self, var):
        local_var = self._findVar(var)
        flags = {}

        if local_var:
            for i in local_var:
                if i == "content":
                    continue
                flags[i] = local_var[i]

        if len(flags) == 0:
            return None
        return flags


    def delVarFlags(self, var, filename = None, lineno = None):
        if not var in self.dict:
            self._makeShadowCopy(var)

        if var in self.dict:
            content = None

            filename, lineno = self.infer_file_and_line(filename, lineno)
            self.eventLog(var, 'clear all flags', '', filename, lineno)
            # try to save the content
            if "content" in self.dict[var]:
                content  = self.dict[var]["content"]
                self.dict[var]            = {}
                self.dict[var]["content"] = content
            else:
                del self.dict[var]


    def createCopy(self):
        """
        Create a copy of self by setting _data to self
        """
        # we really want this to be a DataSmart...
        data = DataSmart(seen=self._seen_overrides.copy(), special=self._special_values.copy())
        data.dict["_data"] = self.dict
        if self._tracking_enabled:
            data._tracking_enabled = self._tracking_enabled
            data.history = copy.deepcopy(self.history)
            data.include_history = copy.deepcopy(self.include_history)
            data.include_stack = []
            oldref = self.include_history
            newref = data.include_history
            # Create corresponding references, if we can
            try:
                for item in self.include_stack:
                    if item[0] >= 0:
                        newref = newref[item[0]][1]
                    newevent = (item[0], newref)
                    data.include_stack.append(newevent)
            except Exception:
                sys.exc_clear()
        return data

    def expandVarref(self, variable, parents=False, filename = None, lineno = None):
        """Find all references to variable in the data and expand it
           in place, optionally descending to parent datastores."""

        if parents:
            keys = iter(self)
        else:
            keys = self.localkeys()

        filename, lineno = self.infer_file_and_line(filename, lineno)
        ref = '${%s}' % variable
        value = self.getVar(variable, False)
        for key in keys:
            referrervalue = self.getVar(key, False)
            if referrervalue and ref in referrervalue:
                self.setVar(key, referrervalue.replace(ref, value), filename, lineno, 'expandVarref')

    def localkeys(self):
        for key in self.dict:
            if key != '_data':
                yield key

    def __iter__(self):
        def keylist(d):        
            klist = set()
            for key in d:
                if key == "_data":
                    continue
                if not d[key]:
                    continue
                klist.add(key)

            if "_data" in d:
                klist |= keylist(d["_data"])

            return klist

        for k in keylist(self.dict):
             yield k

    def __len__(self):
        return len(frozenset(self))

    def __getitem__(self, item):
        value = self.getVar(item, False)
        if value is None:
            raise KeyError(item)
        else:
            return value

    def __setitem__(self, var, value):
        self.setVar(var, value)

    def __delitem__(self, var):
        self.delVar(var)

    def get_hash(self):
        data = {}
        config_whitelist = set((self.getVar("BB_HASHCONFIG_WHITELIST", True) or "").split())
        keys = set(key for key in iter(self) if not key.startswith("__"))
        for key in keys:
            if key in config_whitelist:
                continue
            value = self.getVar(key, False) or ""
            data.update({key:value})

        data_str = str([(k, data[k]) for k in sorted(data.keys())])
        return hashlib.md5(data_str).hexdigest()

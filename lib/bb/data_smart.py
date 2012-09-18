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

import copy, re, sys, traceback
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

def infer_caller_details(loginfo, parent = False):
    """Save the caller the trouble of specifying everything."""
    locals = None
    # Save effort.
    if 'ignore' in loginfo and loginfo['ignore']:
        return
    # If nothing was provided, mark this as possibly unneeded.
    if not loginfo:
        loginfo['ignore'] = True
        return
    if parent:
        depth = 4
    else:
        depth = 3
    # Infer caller's likely values for variable (var), loginfo (loginfo),
    # and value (value), to reduce clutter in the rest of the code.
    if 'variable' not in loginfo or 'value' not in loginfo:
        try:
            raise Exception
        except Exception:
            tb = sys.exc_info()[2]
            if parent:
                above = tb.tb_frame.f_back.f_back
            else:
                above = tb.tb_frame.f_back
            locals = above.f_locals.items()
            tb = None
            above = None
        value = None
        variable = None
        for k, v in locals:
            if k == 'value':
                value = v
            if k == 'var':
                variable = v
        if 'value' not in loginfo:
            loginfo['value'] = value
        if 'variable' not in loginfo:
            loginfo['variable'] = variable
        locals = None
    # Infer file/line/function from traceback
    if 'file' not in loginfo:
        file, line, func, text = traceback.extract_stack(limit = depth)[0]
        loginfo['file'] = file
        loginfo['line'] = line
        if func not in loginfo:
            loginfo['func'] = func

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
            if expression:
                self.msg = "Failure expanding variable %s, expression was %s which triggered exception %s: %s" % (varname, expression, type(exception).__name__, exception)
            else:
                self.msg = "Failure expanding variable %s: %s: %s" % (varname, type(exception).__name__, exception)
        else:
            self.msg = "Failure expanding expression %s which triggered exception %s: %s" % (expression, type(exception).__name__, exception)
        Exception.__init__(self, self.msg)
        self.args = (varname, expression, exception)
    def __str__(self):
        return self.msg

class IncludeHistory(object):
    def __init__(self, parent = None, filename = None, datasmart = None):
        self.parent = parent
        if parent is not None:
            self.top = parent.top
        else:
            self.top = self
        self.datasmart = datasmart
        self.filename = filename or '[TOP LEVEL]'
        self.children = []
        self.current = self
        self.variables = {}

    def include(self, filename):
        newfile = IncludeHistory(self.current, filename)
        self.current.children.append(newfile)
        self.current = newfile
        return self

    def record(self, *kwonly, **loginfo):
        if len(kwonly) > 0:
            raise TypeError
        if not self.top.datasmart._tracking:
            return
        infer_caller_details(loginfo, parent = True)
        if 'ignore' in loginfo and loginfo['ignore']:
            return
        if 'op' not in loginfo or not loginfo['op']:
            loginfo['op'] = 'set'
        if 'details' in loginfo and loginfo['details']:
            loginfo['details'] = str(loginfo['details'])
        if 'value' in loginfo and loginfo['value']:
            loginfo['value'] = str(loginfo['value'])
        if 'variable' not in loginfo or 'file' not in loginfo:
            raise ValueError("record() missing variable or file.")
        var = loginfo['variable']

        if var not in self.variables:
            self.variables[var] = []
        self.variables[var].append(loginfo.copy())

    def variable(self, var):
        if var in self.variables:
            return self.variables[var]
        else:
            return []

    def __enter__(self):
        pass

    def __exit__(self, a, b, c):
        if self.current.parent:
            self.current = self.current.parent
        else:
            bb.warn("Include log: Tried to finish '%s' at top level." % filename)
        return False

    def emit(self, o, level = 0):
        """Emit an include history file, and its children."""
        if self != self.top:
            spaces = "  " * level
            o.write("# %s%s" % (spaces, self.filename))
            if len(self.children) > 0:
                o.write(" includes:")
            level = level + 1
        else:
            o.write("#\n# INCLUDE HISTORY:\n#")
        for child in self.children:
            o.write("\n")
            child.emit(o, level)


class DataSmart(MutableMapping):
    def __init__(self, special = COWDictBase.copy(), seen = COWDictBase.copy() ):
        self.dict = {}

        # cookie monster tribute
        self._special_values = special
        self._seen_overrides = seen
        self.history = IncludeHistory(datasmart = self)
        self._tracking = False

        self.expand_cache = {}

    def enableTracking(self):
        self._tracking = True

    def disableTracking(self):
        self._tracking = False

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


    def finalize(self, parent = False):
        """Performs final steps upon the datastore, including application of overrides"""

        overrides = (self.getVar("OVERRIDES", True) or "").split(":") or []
        finalize_caller = {
            'variable': 'ignored',
            'value': 'ignored',
            'op': 'finalize',
        }
        infer_caller_details(finalize_caller, parent = parent)

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

        # We only want to report finalization once per variable overridden.
        finalizes_reported = {}

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
                    # Report only once, even if 
                    if name not in finalizes_reported:
                        finalizes_reported[name] = True
                        finalize_caller['variable'] = name
                        finalize_caller['value'] = 'was: ' + str(self.getVar(name, False))
                        self.history.record(**finalize_caller)
                    # Copy history of the override over.
                    for event in self.history.variable(var):
                        loginfo = event.copy()
                        loginfo['variable'] = name
                        loginfo['op'] = 'override[%s]:%s' % (o, loginfo['op'])
                        self.history.record(**loginfo)
                    self.setVar(name, self.getVar(var, False), op = 'finalize', file = 'override[%s]' % o, line = '')
                    self.delVar(var)
                except Exception:
                    logger.info("Untracked delVar")

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
                            self.setVar(append, sval)
                        elif op == "_prepend":
                            sval = a + (self.getVar(append, False) or "")
                            self.setVar(append, sval)

                    # We save overrides that may be applied at some later stage
                    if keep:
                        self.setVarFlag(append, op, keep)
                    else:
                        self.delVarFlag(append, op)

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


    def setVar(self, var, value, **loginfo):
        infer_caller_details(loginfo)
        self.expand_cache = {}
        match  = __setvar_regexp__.match(var)
        if match and match.group("keyword") in __setvar_keyword__:
            base = match.group('base')
            keyword = match.group("keyword")
            override = match.group('add')
            l = self.getVarFlag(base, keyword) or []
            l.append([value, override])
            self.setVarFlag(base, keyword, l)
            # And cause that to be recorded:
            loginfo['details'] = value
            loginfo['variable'] = base
            if override:
                loginfo['op'] = '%s[%s]' % (keyword, override)
            else:
                loginfo['op'] = keyword
            self.history.record(**loginfo)
            # todo make sure keyword is not __doc__ or __module__
            # pay the cookie monster
            try:
                self._special_values[keyword].add(base)
            except KeyError:
                self._special_values[keyword] = set()
                self._special_values[keyword].add(base)

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
        self.dict[var]["_content"] = value
        self.history.record(**loginfo)

    def getVar(self, var, expand=False, noweakdefault=False):
        value = self.getVarFlag(var, "_content", False, noweakdefault)

        # Call expand() separately to make use of the expand cache
        if expand and value:
            return self.expand(value, var)
        return value

    def renameVar(self, key, newkey, **loginfo):
        """
        Rename the variable key to newkey
        """
        val = self.getVar(key, 0)
        if val is not None:
            loginfo['op'] = 'rename'
            loginfo['details'] = key
            self.setVar(newkey, val, **loginfo)

        for i in ('_append', '_prepend'):
            src = self.getVarFlag(key, i)
            if src is None:
                continue

            dest = self.getVarFlag(newkey, i) or []
            dest.extend(src)
            self.setVarFlag(newkey, i, dest)

            if i in self._special_values and key in self._special_values[i]:
                self._special_values[i].remove(key)
                self._special_values[i].add(newkey)

        self.delVar(key)

    def appendVar(self, key, value, **loginfo):
        loginfo['details'] = value
        value = (self.getVar(key, False) or "") + value
        self.setVar(key, value, **loginfo)

    def prependVar(self, key, value, **loginfo):
        loginfo['details'] = value
        value = value + (self.getVar(key, False) or "")
        self.setVar(key, value, **loginfo)

    def delVar(self, var, **loginfo):
        loginfo['value'] = ""
        if not 'op' in loginfo:
            loginfo['op'] = 'del'
        self.history.record(**loginfo)
        self.expand_cache = {}
        self.dict[var] = {}
        if '_' in var:
            override = var[var.rfind('_')+1:]
            if override and override in self._seen_overrides and var in self._seen_overrides[override]:
                self._seen_overrides[override].remove(var)

    def setVarFlag(self, var, flag, flagvalue, **loginfo):
        infer_caller_details(loginfo)
        loginfo['value'] = flagvalue
        loginfo['flag'] = flag
        self.history.record(**loginfo)
        if not var in self.dict:
            self._makeShadowCopy(var)
        self.dict[var][flag] = flagvalue

    def getVarFlag(self, var, flag, expand=False, noweakdefault=False):
        local_var = self._findVar(var)
        value = None
        if local_var:
            if flag in local_var:
                value = copy.copy(local_var[flag])
            elif flag == "_content" and "defaultval" in local_var and not noweakdefault:
                value = copy.copy(local_var["defaultval"])
        if expand and value:
            value = self.expand(value, None)
        return value

    def delVarFlag(self, var, flag, **loginfo):
        infer_caller_details(loginfo)
        loginfo['value'] = ""
        local_var = self._findVar(var)
        if 'op' not in loginfo:
            loginfo['op'] = 'delFlag'
        loginfo['flag'] = flag
        if not local_var:
            return
        if not var in self.dict:
            self._makeShadowCopy(var)

        if var in self.dict and flag in self.dict[var]:
            self.history.record(**loginfo)
            del self.dict[var][flag]

    def appendVarFlag(self, key, flag, value, **loginfo):
        infer_caller_details(loginfo)
        loginfo['details'] = value
        value = (self.getVarFlag(key, flag, False) or "") + value
        self.setVarFlag(key, flag, value, **loginfo)

    def prependVarFlag(self, key, flag, value, **loginfo):
        infer_caller_details(loginfo)
        loginfo['details'] = value
        value = value + (self.getVarFlag(key, flag, False) or "")
        self.setVarFlag(key, flag, value, **loginfo)

    def setVarFlags(self, var, flags, **loginfo):
        infer_caller_details(loginfo)
        if not var in self.dict:
            self._makeShadowCopy(var)

        for i in flags:
            if i == "_content":
                continue
            loginfo['flag'] = i
            self.history.record(**loginfo)
            self.dict[var][i] = flags[i]

    def getVarFlags(self, var):
        local_var = self._findVar(var)
        flags = {}

        if local_var:
            for i in local_var:
                if i.startswith("_"):
                    continue
                flags[i] = local_var[i]

        if len(flags) == 0:
            return None
        return flags


    def delVarFlags(self, var, **loginfo):
        infer_caller_details(loginfo)
        if 'op' not in loginfo:
            loginfo['op'] = 'delete flags'
        if not var in self.dict:
            self._makeShadowCopy(var)

        if var in self.dict:
            content = None
            self.history.record(**loginfo)

            # try to save the content
            if "_content" in self.dict[var]:
                content  = self.dict[var]["_content"]
                self.dict[var]            = {}
                self.dict[var]["_content"] = content
            else:
                del self.dict[var]

    def createCopy(self):
        """
        Create a copy of self by setting _data to self
        """
        # we really want this to be a DataSmart...
        data = DataSmart(seen=self._seen_overrides.copy(), special=self._special_values.copy())
        data.dict["_data"] = self.dict
        data.history = copy.deepcopy(self.history)
        data.history.datasmart = data
        data._tracking = self._tracking

        return data

    def expandVarref(self, variable, parents=False):
        """Find all references to variable in the data and expand it
           in place, optionally descending to parent datastores."""

        if parents:
            keys = iter(self)
        else:
            keys = self.localkeys()

        ref = '${%s}' % variable
        value = self.getVar(variable, False)
        for key in keys:
            referrervalue = self.getVar(key, False)
            if referrervalue and ref in referrervalue:
                self.setVar(key, referrervalue.replace(ref, value))

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

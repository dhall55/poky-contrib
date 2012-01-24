# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright 2012 Intel Corporation
# Authored-by:  Tom Zanussi <tom.zanussi@intel.com>
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

import os
import sys
import logging
from abc import ABCMeta, abstractmethod
from tags import *


class Line():
    """
    Generic (abstract) container representing a line that will appear
    in the BSP-generating program.
    """
    __metaclass__ = ABCMeta
    optional_input = None

    def __init__(self, line):
        self.line = line
        self.generated_line = ""

    @abstractmethod
    def gen(self):
        """
        Generate the final executable line that will appear in the
        BSP-generation program.
        """
        pass

    def escape(self, line):
        """
        Escape single and double quotes and backslashes until I find
        something better (re.escape() escapes way too much)
        """
        return line.replace("\\", "\\\\").replace("\"", "\\\"").replace("'", "\\'")

    def parse_error(self, msg, lineno, line):
         raise SyntaxError("%s: %s" % (msg, line))


class NormalLine(Line):
    """
    Container for normal (non-tag) lines.
    """
    def __init__(self, line):
        Line.__init__(self, line)
        self.is_filename = False
        self.is_dirname = False
        self.out_filebase = None

    def gen(self):
        if self.is_filename:
            line = "of = open(\"" + os.path.join(self.out_filebase, self.escape(self.line)) + "\", \"w\")"
        elif self.is_dirname:
            dirname = os.path.join(self.out_filebase, self.escape(self.line))
            line = "if not os.path.exists(\"" + dirname + "\"): os.mkdir(\"" + dirname + "\")"
        else:
            line = "of.write(\"" + self.escape(self.line) + "\\n\")"
        return line


class CodeLine(Line):
    """
    Container for Python code tag lines.
    """
    def __init__(self, line):
        Line.__init__(self, line)

    def gen(self):
        return self.line


class Assignment:
    """
    Representation of everything we know about {{=name }} tags.
    Instances of these are used by Assignment lines.
    """
    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.name = name


class AssignmentLine(NormalLine):
    """
    Container for normal lines containing assignment tags.  Assignment
    tags must be in ascending order of 'start' value.
    """
    def __init__(self, line):
        NormalLine.__init__(self, line)
        self.assignments = []

    def add_assignment(self, start, end, name):
        self.assignments.append(Assignment(start, end, name))

    def gen(self):
        line = self.escape(self.line)
        for assignment in self.assignments:
            replacement = "\" + " + assignment.name + " + \""
            idx = line.find(ASSIGN_TAG)
            line = line[:idx] + replacement + line[idx + assignment.end - assignment.start:]
        # todo, atm escaping prevents reuse, maybe refactor using mixins
        if self.is_filename:
            return "of = open(\"" + os.path.join(self.out_filebase, line) + "\", \"w\")"
        elif self.is_dirname:
            dirname = os.path.join(self.out_filebase, line)
            return "if not os.path.exists(\"" + dirname + "\"): os.mkdir(\"" + dirname + "\")"
        else:
            return "of.write(\"" + line + "\\n\")"


class InputLine(Line):
    """
    Base class for Input lines.
    """
    def __init__(self, props, tag, lineno):
        Line.__init__(self, tag)
        self.props = props
        self.lineno = lineno
        try:
            self.prio = int(props["prio"])
        except KeyError:
            self.prio = sys.maxint

    def gen(self):
        try:
            depends_on = self.props["depends-on"]
            try:
                depends_on_val = self.props["depends-on-val"]
            except KeyError:
                self.parse_error("No 'depends-on-val' for 'depends-on' property",
                                 self.lineno, self.line)
        except KeyError:
            pass


class BooleanInputLine(InputLine):
    """
    Base class for boolean Input lines.
    props:
        name: example - "keyboard"
        msg:  example - "Got keyboard?"
    result:
        Sets the value of the variable specified by 'name' to "yes" or "no"
        example - keyboard = "yes"
    """
    def __init__(self, props, tag, lineno):
        InputLine.__init__(self, props, tag, lineno)

    def query_user(self):
        msg = self.props["name"]
        if not msg:
            self.parse_error("No input 'msg' property found",
                             self.lineno, self.line)
        return self.show_prompt(msg)

    def gen(self):
        InputLine.gen(self)
        name = self.props["name"]
        if not name:
            self.parse_error("No input 'name' property found",
                             self.lineno, self.line)
        msg = self.props["msg"]
        if not msg:
            self.parse_error("No input 'msg' property found",
                             self.lineno, self.line)

        if Line.optional_input:
            line = name + " = \"" + Line.optional_input[name] + "\""
        else:
            line = name + " = lower1(raw_input(\"\"\"" + msg + " \"\"\"))"

        return line


class ListInputLine(InputLine):
    """
    Base class for List-based Input lines. e.g. Choicelist, Checklist
    """
    __metaclass__ = ABCMeta

    def __init__(self, props, tag, lineno):
        InputLine.__init__(self, props, tag, lineno)
        self.choices = []

    def gen_choicepair_list(self):
        """generate a list of 2-item val:desc lists from self.choices"""
        if not self.choices:
            return None
        choicepair_list = list()
        for choice in self.choices:
            choicepair = []
            choicepair.append(choice.val)
            choicepair.append(choice.desc)
            choicepair_list.append(choicepair)
        return choicepair_list

    def gen_degenerate_choicepair_list(self, choices):
        """generate a list of 2-item val:desc with val=desc from passed-in choices"""
        choicepair_list = list()
        for choice in choices:
            choicepair = []
            choicepair.append(choice)
            choicepair.append(choice)
            choicepair_list.append(choicepair)
        return choicepair_list

    def exec_listgen_fn(self):
        retval = None
        try:
            fname = self.props["gen"]
            modsplit = fname.split('.')
            mod_fn = modsplit.pop()
            mod = '.'.join(modsplit)

            __import__(mod)
            # python 2.7 has a better way to do this using importlib.import_module
            m = sys.modules[mod]

            fn = getattr(m, mod_fn)
            if not fn:
                self.parse_error("couldn't load function specified for 'gen' property ",
                                 self.lineno, self.line)
            retval = fn()
            if not retval:
                self.parse_error("function specified for 'gen' property returned nothing ",
                                 self.lineno, self.line)
        except KeyError:
            pass
        return retval

    @abstractmethod
    def gen_choice_assign(self, name, msg, choices_str, choices_valstr):
        """
        Given a string containing the list of choices to print,
        generate an assignment from either a string (for a choicelist)
        or a list (for a checklist) etc.  This needs to be implemented
        by anything inheriting ListInputLine.
        """
        pass

    def gen_choices_str(self, choicepairs):
        """
        Generate a numbered list of choices from a list of choicepairs
        for display to the user.
        """
        choices_str = ""
        for i, choicepair in enumerate(choicepairs):
            choices_str += "\t" + str(i + 1) + ") " + choicepair[1] + "\n"
        return choices_str

    def gen_choices_val_str(self, choicepairs):
        """
        Generate an array of choice values corresponding to the
        numbered list generated by gen_choices_str().
        """
        choices_val_list = "["
        for i, choicepair in enumerate(choicepairs):
            choices_val_list += "\"" + choicepair[0] + "\","
        choices_val_list += "]"

        return choices_val_list

    def gen_choices(self):
        name = self.props["name"]
        if not name:
            self.parse_error("No input 'name' property found",
                             self.lineno, self.line)

        msg = self.props["msg"]
        if not msg:
            self.parse_error("No input 'msg' property found",
                             self.lineno, self.line)

        if Line.optional_input:
            line = name + " = \"" + Line.optional_input[name] + "\""
        else:
            choices_str = None
            choices = self.exec_listgen_fn()
            if choices:
                if len(choices) == 0:
                    self.parse_error("No entries available for input list",
                                     self.lineno, self.line)
                choicepairs = self.gen_degenerate_choicepair_list(choices)
            else:
                if len(self.choices) == 0:
                    self.parse_error("No entries available for input list",
                                     self.lineno, self.line)
                choicepairs = self.gen_choicepair_list()

            choices_str = self.gen_choices_str(choicepairs)
            choices_val_str = self.gen_choices_val_str(choicepairs)
            line = self.gen_choice_assign(name, msg, choices_str, choices_val_str)

        return line

def lower1(input_str):
    """
    Return lowercase version of first char in string.
    """
    str = input_str.lower().strip()
    if str:
        return str[0]

    return None


def find_choiceval(choice_str, choice_list):
    """
    Take number as string and return val string from choice_list,
    empty string if oob.  choice_list is a simple python list.
    """
    choice_val = ""
    choice_idx = int(choice_str)
    if choice_idx <= len(choice_list):
        choice_idx -= 1
        choice_val = choice_list[choice_idx]

    return choice_val


def find_choicevals(choice_str, choice_list):
    """
    Take numbers as space-separated string and return vals list from
    choice_list, empty list if oob.  choice_list is a simple python
    list.
    """
    choice_vals = []
    choices = choice_str.split()
    for choice in choices:
        choice_vals.append(find_choiceval(choice, choice_list))

    return choice_vals


class ChoicelistInputLine(ListInputLine):
    """
    Base class for choicelist Input lines.
    props:
        name: example - "xserver_choice"
        msg:  example - "Please select an xserver for this machine"
    result:
        Sets the value of the variable specified by 'name' to whichever Choice was chosen
        example - xserver_choice = "xserver_vesa"
    """
    def __init__(self, props, tag, lineno):
        ListInputLine.__init__(self, props, tag, lineno)

    def gen_choice_assign(self, name, msg, choices_str, choices_val_str):
        """
        Called by gen_choices() in ListInputLine.
        """
        line = name + " = find_choiceval(raw_input(\"\"\"" + msg + "\n" + choices_str + "\"\"\")," + choices_val_str + ")"
        return line

    def gen(self):
        InputLine.gen(self)

        return self.gen_choices()


class ListValInputLine(InputLine):
    """
    Abstract base class for choice and checkbox Input lines.
    """
    def __init__(self, props, tag, lineno):
        InputLine.__init__(self, props, tag, lineno)

        try:
            self.val = self.props["val"]
        except KeyError:
            self.parse_error("No input 'val' property found", self.lineno, self.line)

        try:
            self.desc = self.props["msg"]
        except KeyError:
            self.parse_error("No input 'msg' property found", self.lineno, self.line)


class ChoiceInputLine(ListValInputLine):
    """
    Base class for choice Input lines.
    """
    def __init__(self, props, tag, lineno):
        ListValInputLine.__init__(self, props, tag, lineno)

    def gen(self):
        return None


class ChecklistInputLine(ListInputLine):
    """
    Base class for checklist Input lines.
    """
    def __init__(self, props, tag, lineno):
        ListInputLine.__init__(self, props, tag, lineno)

    def gen_choice_assign(self, name, msg, choices_str, choices_val_str):
        """
        Called by gen_choices() in ListInputLine.
        """
        line = name + " = find_choicevals(raw_input(\"\"\"" + msg + "\n" + choices_str + "\"\"\")," + choices_val_str + ")"
        return line

    def gen(self):
        InputLine.gen(self)

        return self.gen_choices()


class CheckInputLine(ListValInputLine):
    """
    Base class for check Input lines.
    """
    def __init__(self, props, tag, lineno):
        ListValInputLine.__init__(self, props, tag, lineno)

    def gen(self):
        return None


class SubstrateBase(object):
    """
    Container for both expanded and unexpanded substrate objects.
    """
    def __init__(self, filename, filebase, out_filebase):
        self.filename = filename
        self.filebase = filebase # beginning part to discard
        self.out_filebase = out_filebase # base output dir e.g. 'meta-foo', can be absolute
        self.raw_lines = []
        self.expanded_lines = [] # Lines
        self.prev_choicelist = None

    def parse_error(self, msg, lineno, line):
         raise SyntaxError("%s: [%s: %d]: %s" % (msg, self.filename, lineno, line))

    def expand_input_tag(self, tag, lineno):
        """
        Input tags consist of the word 'input' at the beginning,
        followed by name:value pairs which are converted into a
        dictionary.
        """
        propstr = tag[len(INPUT_TAG):]

        import shlex
        # todo: this will break if there's a : in a string e.g. "choose:"
        props = dict(prop.split(":") for prop in shlex.split(propstr))

        input_type = props[INPUT_TYPE_PROPERTY]
        if not props[INPUT_TYPE_PROPERTY]:
            self.parse_error("No input 'type' property found", lineno, tag)

        if input_type == "boolean":
            return BooleanInputLine(props, tag, lineno)
        elif input_type == "choicelist":
            self.prev_choicelist = ChoicelistInputLine(props, tag, lineno)
            return self.prev_choicelist
        elif input_type == "choice":
            if not self.prev_choicelist:
                self.parse_error("Found 'choice' input tag but no previous choicelist",
                                 lineno, tag)
            choice = ChoiceInputLine(props, tag, lineno)
            self.prev_choicelist.choices.append(choice)
            return choice
        elif input_type == "checklist":
            return ChecklistInputLine(props, tag, lineno)
        elif input_type == "check":
            return CheckInputLine(props, tag, lineno)

    def expand_assignment_tag(self, start, line, lineno):
        """
        Expand all tags in a line
        """
        expanded_line = AssignmentLine(line.strip())

        while start != -1:
            end = line.find(CLOSE_TAG, start)
            if end == -1:
                self.parse_error("No close tag found for assign tag", lineno, line)
            else:
                name = line[start + len(ASSIGN_TAG):end].strip()
                expanded_line.add_assignment(start, end + len(CLOSE_TAG), name)
                start = line.find(ASSIGN_TAG, end)

        return expanded_line

    def expand_tag(self, line, lineno):
        """
        Returns a processed tag line, or None if there was no tag

        The rules for tags are very simple:
            - No nested tags
            - Tags start with {{ and end with }}
            - An assign tag, {{=, can appear anywhere and will
              be replaced with what the assignment evaluates to
            - Any other tag occupies the whole line it is on
                - if there's anything else on the tag line, it's an error
                - if it starts with 'input', it's an input tag and
                  will only be used for prompting and setting variables
                - anything else is straight Python
                - tags are in effect only until the next blank line or tag or 'pass' tag
                - we don't have indentation in tags, but we need some way to end a block
                  forcefully without blank lines or other tags - that's the 'pass' tag
                - todo: implement pass tag
                - directories and filenames can have tags as well, but only assignment
                  and 'if' code lines
                - directories and filenames are the only case where normal tags can
                  coexist with normal text on the same 'line'
        """
        start = line.find(ASSIGN_TAG)
        if start != -1:
            return self.expand_assignment_tag(start, line, lineno)

        start = line.find(OPEN_TAG)
        if start == -1:
            return None

        end = line.find(CLOSE_TAG, 0)
        if end == -1:
             self.parse_error("No close tag found for open tag", lineno, line)

        tag = line[start + len(OPEN_TAG):end].strip()

        if not tag.lstrip().startswith(INPUT_TAG):
            return CodeLine(tag)

        return self.expand_input_tag(tag, lineno)


    def expand_file_or_dir_name(self):
        """
        Expand file or dir names into codeline.  Dirnames and
        filenames can only have assignments or if statements.  First
        translate if statements into CodeLine + (dirname or filename
        creation).
        """
        lineno = 0
        line = self.filename[len(self.filebase):]
        if line.startswith("/"):
            line = line[1:]
        opentag_start = -1
        start = line.find(OPEN_TAG)
        while start != -1:
            if not line[start:].startswith(ASSIGN_TAG):
                opentag_start = start
                break
            start += len(ASSIGN_TAG)
            start = line.find(OPEN_TAG, start)

        if opentag_start != -1:
            end = line.find(CLOSE_TAG, opentag_start)
            if end == -1:
                self.parse_error("No close tag found for open tag", lineno, line)
            # we have a {{ tag i.e. code
            tag = line[opentag_start + len(OPEN_TAG):end].strip()

            if not tag.lstrip().startswith(IF_TAG):
                self.parse_error("Only 'if' tags are allowed in file or directory names",
                                 lineno, line)
            self.expanded_lines.append(CodeLine(tag))

            # everything after }} is the actual filename (possibly with assignments)
            # everything before is the pathname
            line = line[:opentag_start] + line[end + len(CLOSE_TAG):].strip()

        assign_start = line.find(ASSIGN_TAG)
        if assign_start != -1:
            # get rid of flags, refactor, todo
            assignment_tag = self.expand_assignment_tag(assign_start, line, lineno)
            if isinstance(self, SubstrateFile):
                assignment_tag.is_filename = True
                assignment_tag.out_filebase = self.out_filebase
            elif isinstance(self, SubstrateDir):
                assignment_tag.is_dirname = True
                assignment_tag.out_filebase = self.out_filebase
            self.expanded_lines.append(assignment_tag)
            return

        normal_line = NormalLine(line)
        if isinstance(self, SubstrateFile):
            normal_line.is_filename = True
            normal_line.out_filebase = self.out_filebase
        elif isinstance(self, SubstrateDir):
            normal_line.is_dirname = True
            normal_line.out_filebase = self.out_filebase
        self.expanded_lines.append(normal_line)


    def expand(self):
        """
        Expand the file or dir name first, eventually this ends up
        creating the file or dir.
        """
        self.expand_file_or_dir_name()


class SubstrateFile(SubstrateBase):
    """
    Container for both expanded and unexpanded substrate files.
    """
    def __init__(self, filename, filebase, out_filebase):
        SubstrateBase.__init__(self, filename, filebase, out_filebase)

    def read(self):
        if self.raw_lines:
            return
        f = open(self.filename)
        self.raw_lines = f.readlines()

    def expand(self):
        """Expand the contents of all template tags in the file"""
        SubstrateBase.expand(self)
        self.read()
        for lineno, line in enumerate(self.raw_lines):
            expanded_line = self.expand_tag(line, lineno + 1) # humans not 0-based
            if not expanded_line:
                expanded_line = NormalLine(line.rstrip())
            self.expanded_lines.append(expanded_line)

    def gen(self):
        """Generate the code that generates the BSP."""
        indent = new_indent = 0
        for line in self.expanded_lines:
            genline = line.gen()
            if not genline:
                continue
            if isinstance(line, InputLine):
                line.generated_line = genline
                continue
            if indent:
                if genline == BLANKLINE_STR or (not genline.startswith(NORMAL_START)
                                                and not genline.startswith(OPEN_START)):
                    indent = new_indent = 0
            if genline.endswith(":"):
                new_indent = 1
            line.generated_line = (indent * INDENT_STR) + genline
            indent = new_indent


class SubstrateDir(SubstrateBase):
    """
    Container for both expanded and unexpanded substrate dirs.
    """
    def __init__(self, filename, filebase, out_filebase):
        SubstrateBase.__init__(self, filename, filebase, out_filebase)

    def expand(self):
        SubstrateBase.expand(self)

    def gen(self):
        """generate the code that generates the BSP."""
        indent = new_indent = 0
        for line in self.expanded_lines:
            genline = line.gen()
            if not genline:
                continue
            if genline.endswith(":"):
                new_indent = 1
            else:
                new_indent = 0
            line.generated_line = (indent * INDENT_STR) + genline
            indent = new_indent


def expand_target(target, all_files, out_filebase):
    """
    Expand the contents of all template tags in the target.  This
    means removing tags and categorizing or creating lines so that
    future passes can process and present input lines and generate the
    corresponding lines of the Python program that will be exec'ed to
    actually produce the final BSP.  'all_files' includes directories.
    """
    for root, dirs, files in os.walk(target):
        for file in files:
            if file.endswith("~") or file.endswith("#"):
                continue
            f = os.path.join(root, file)
            sfile = SubstrateFile(f, target, out_filebase)
            sfile.expand()
            all_files.append(sfile)
        for dir in dirs:
            d = os.path.join(root, dir)
            sdir = SubstrateDir(d, target, out_filebase)
            sdir.expand()
            all_files.append(sdir)


def gen_program_machine_lines(machine, program_lines):
    """
    Use the input values we got from the command line.
    """
    line = "machine = \"" + machine + "\""
    program_lines.append(line)


def sort_inputlines(input_lines):
    """Sort input lines according to priority (position)"""
    input_lines.sort(key = lambda l: l.prio)


def find_parent_dependency(lines, depends_on):
    for i, line in lines:
        if isinstance(line, CodeLine):
            continue
        if line.props["name"] == depends_on:
            return i
    return -1

def process_inputline_dependencies(input_lines, all_inputlines):
    """If any input lines depend on others, put the others first"""
    """todo: use find_parent_dependency and arrange things appropriately"""
    """for now, we rely on prio ordering being correct"""
    for line in input_lines:
        try:
            depends_on = line.props["depends-on"]
            depends_codeline = "if " + line.props["depends-on"] + " == \"" + line.props["depends-on-val"] + "\":"
            all_inputlines.append(CodeLine(depends_codeline))
            all_inputlines.append(line)
        except KeyError:
            all_inputlines.append(line)


def gather_inputlines(files, all_inputlines):
    """Gather all the InputLines - we want to generate them first"""
    input_lines = []
    for file in files:
        if isinstance(file, SubstrateFile):
            for line in file.expanded_lines:
                if isinstance(line, InputLine):
                    input_lines.append(line)

    sort_inputlines(input_lines)
    process_inputline_dependencies(input_lines, all_inputlines)


def run_program_lines(linelist, codedump):
    """for a single file, print all the python code into a buf and try execing it"""
    buf = "\n".join(linelist)
    if codedump:
        of = open("bspgen.out", "w")
        of.write(buf)
        of.close()
    exec buf


def gen_target(files):
    """Generate the python code for each file"""
    for file in files:
        file.gen()


def gen_program_header_lines(input_lines, program_lines):
    """
    Generate the basic imports we need, along with null entries for
    input values, so we don't have undefined variables
    """
    for line in input_lines:
        if isinstance(line, InputLine):
            try:
                name = line.props["name"]
                program_line = name + " = \"\"" 
                program_lines.append(program_line)
            except KeyError:
                pass


def gen_program_input_lines(input_lines, program_lines):
    """We only have input lines and CodeLines affecting the next input line"""
    indent = new_indent = 0
    for line in input_lines:
        genline = line.gen()
        if not genline:
            continue
        if genline.endswith(":"):
            new_indent = 1
        else:
            new_indent = 0

        line.generated_line = (indent * INDENT_STR) + genline
        program_lines.append(line.generated_line)

        indent = new_indent


def gen_program_lines(target_files, program_lines):
    """
    Append the generated lines of all target_files to program_lines.
    Skip input lines.
    """
    for file in target_files:
        for line in file.expanded_lines:
            if isinstance(line, InputLine):
                continue
            program_lines.append(line.generated_line)


def yocto_bsp_create(machine, arch, scripts_path, bsp_output_dir, codedump):
    """
    create bsp

    machine - user-defined machine name
    arch - the arch the bsp will be based on, must be one in
           scripts/lib/bsp/substrate/target/arch
    scripts_path - absolute path to yocto /scripts dir
    bsp_output_dir - dirname to create for BSP
    codegen - dump generated code to bspgen.out
    """
    logging.debug("yocto_bsp_create")

    if os.path.exists(bsp_output_dir):
        print "\nBSP output dir already exists, exiting. (%s)" % bsp_output_dir
        sys.exit(1)

    os.mkdir(bsp_output_dir)

    lib_path = scripts_path + '/lib'
    bsp_path = lib_path + '/bsp'
    arch_path = bsp_path + '/substrate/target/arch'
    common = os.path.join(arch_path, "common")

    target_files = []

    expand_target(common, target_files, bsp_output_dir)

    arches = os.listdir(arch_path)
    if arch not in arches or arch == "common":
        logging.error("Invalid karch, exiting\n")
        parser.print_help()
        exit(1)

    target = os.path.join(arch_path, arch)

    expand_target(target, target_files, bsp_output_dir)

    gen_target(target_files)

    input_lines = []

    # We want all input lines at the beginning.  Evaluating those
    # fills in the variables needed by later code.
    gather_inputlines(target_files, input_lines)

    program_lines = []

    gen_program_header_lines(input_lines, program_lines)
    gen_program_machine_lines(machine, program_lines)
    gen_program_input_lines(input_lines, program_lines)
    gen_program_lines(target_files, program_lines)

    run_program_lines(program_lines, codedump)

    print "New %s BSP created in %s" % (arch, bsp_output_dir)


def yocto_bsp_list(args, scripts_path):
    """
    Print available architectures and machine branches
    """
    logging.debug("yocto_bsp_list")

    if not len(args):
        return False

    if args[0] == "karch":
        lib_path = scripts_path + '/lib'
        bsp_path = lib_path + '/bsp'
        arch_path = bsp_path + '/substrate/target/arch'
        print "Architectures available:"
        for arch in os.listdir(arch_path):
            if arch == "common":
                continue
            print "    %s" % arch

    return True



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

import subprocess
import logging


def subcommand_error(args):
    logging.info("invalid subcommand %s" % args[0])


def display_help(subcommand, subcommands):
    if subcommand not in subcommands:
        return False

    help = subcommands.get(subcommand, subcommand_error)[2]
    pager = subprocess.Popen('less', stdin=subprocess.PIPE)
    pager.communicate(help)

    return True


def yocto_help(args, usage_str, subcommands):
    """
    subcommand help dispatcher
    """
    if len(args) == 1 or not display_help(args[1], subcommands):
        print(usage_str)


def invoke_subcommand(args, parser, main_command_usage, subcommands):
    # Dispatch to subcommand handler
    # borrowed from combo-layer
    # should use argparse, but has to work in 2.6
    if not args:
        logging.error("No subcommand specified, exiting")
        parser.print_help()
    elif args[0] == "help":
        yocto_help(args, main_command_usage, subcommands)
    elif args[0] not in subcommands:
        logging.error("Unsupported subcommand %s, exiting\n" % (args[0]))
        parser.print_help()
    else:
        usage = subcommands.get(args[0], subcommand_error)[1]
        subcommands.get(args[0], subcommand_error)[0](args[1:], usage)


##
# yocto-bsp help and usage strings
##

yocto_bsp_usage = """

 Create a customized Yocto BSP layer.

 usage: yocto-bsp [--version] [--help] COMMAND [ARGS]

 The most commonly used 'yocto-bsp' commands are:
    create            Create a new Yocto BSP
    list              List available values for options and BSP properties

 See 'yocto-bsp help COMMAND' for more information on a specific command.
"""

yocto_bsp_create_usage = """

 Create a new Yocto BSP

 usage: yocto-bsp create <bsp-name> <karch> [--outdir <DIRNAME> | -o <DIRNAME>]
            [--property <NAME:VAL> | -p <NAME:VAL>]

 This command creates a Yocto BSP based on the specified parameters.
 The new BSP will be a new Yocto BSP layer contained by default within
 the top-level directory specified as 'meta-bsp-name'.  The -o option
 can be used to place the BSP layer in a directory with a different
 name and location.

 The value of the 'karch' parameter determines the set of files that
 will be generated for the BSP, along with the specific set of
 'properties' that will be used to fill out the BSP-specific portions
 of the BSP.

 The BSP-specific properties that define the values that will be used
 to generate a particular BSP can be specified on the comman-line
 using the --property option for each property, which is a
 colon-separated name:value pair.  If no --property options are given,
 the user will be interactively prompted for each of the required
 property values, which will then be used as values for BSP
 generation.
"""

yocto_bsp_list_usage = """

 usage: yocto-bsp list <karch>
        yocto-bsp list <karch> properties
        yocto-bsp list <karch> property <xxx>

 This command enumerates the complete set of possible values for a
 specified option or property needed by the BSP creation process.

 The first form enumerates all the possible values that exist and can
 be specified for the 'karch' parameter to the 'yocto bsp create'
 command.

 The second form enumerates all the possible properties that exist
 and must have values specified for them in the 'yocto bsp create'
 command for the given 'karch'.

 The third form enumerates all the possible values that exist and
 can be specified for any of the enumerable properties of the given
 'karch' in the 'yocto bsp create' command.
"""

yocto_bsp_help_usage = """

 usage: yocto-bsp help <subcommand>

 This command displays detailed help for the specified subcommand.
"""

yocto_bsp_create_help = """

NAME
    yocto-bsp create - Create a new Yocto BSP

SYNOPSIS
    yocto-bsp create <bsp-name> <karch> [--outdir <DIRNAME> | -o <DIRNAME>]
        [--property <NAME:VAL> | -p <NAME:VAL>]

DESCRIPTION

    This command creates a Yocto BSP based on the specified
    parameters.  The new BSP will be a new Yocto BSP layer contained
    by default within the top-level directory specified as
    'meta-bsp-name'.  The -o option can be used to place the BSP layer
    in a directory with a different name and location.

    The value of the 'karch' parameter determines the set of files
    that will be generated for the BSP, along with the specific set of
    'properties' that will be used to fill out the BSP-specific
    portions of the BSP.

    The BSP-specific properties that define the values that will be
    used to generate a particular BSP can be specified on the
    comman-line using the --property option for each property, which
    is a colon-separated name:value pair.

    The set of properties and enumerations of their possible values
    can be displayed using the 'yocto-bsp list' command.

    It isn't necessary however for the user to explicitly specify the
    property values using --property options - if none are specified
    in the 'yocto-bsp create' invocation, the user will be
    interactively prompted for each of the required property values,
    which will then be used as values for BSP generation.

    The 'kmachine' parameter names the 'machine branch' that the BSP's
    machine branch will be based on; the list of branches meaningful
    for that purpose can also be listed using the 'yocto-bsp list'
    command.

    The 'yocto-bsp list' command can also be used to list the possible
    values for the 'karch' parameter.

    An typical example that would query the user for property values
    would be:

    $ yocto-bsp create meta-foo i386 yocto/standard/common-pc/foo

    Because the user hasn't specified any values for the BSP
    properties, yocto-bsp will query the user for each of the
    unspecified property values required to create the BSP i.e. the
    properties listed by 'yocto-bsp list properties'.

    Here's an example using explicitly-specified properties:

    $ yocto-bsp create meta-foo i386 yocto/standard/common-pc/foo
       --property tunefile:tune-atom --property touchscreen:true
       --property kfeature:cfg/smp [...]
"""

yocto_bsp_list_help = """

NAME
    yocto-bsp list - List available values for options and BSP properties

SYNOPSIS
    yocto-bsp list <karch | kmachine>
    yocto-bsp list <karch> properties
    yocto-bsp list <karch> property <xxx>

DESCRIPTION
    This command enumerates the complete set of possible values for a
    specified option or property needed by the BSP creation process.

    The first form enumerates all the possible values that exist and
    can be specified for the 'karch' or 'kmachine' parameters to the
    'yocto bsp create' command.  Example output for those options:

     $ yocto-bsp list karch
         i386
         x86_64
         arm
         powerpc
         mips

     $ yocto-bsp list kmachine
         yocto
         yocto/standard
         yocto/standard/common-pc
         yocto/standard/common-pc-64
         yocto/standard/preempt-rt

    The second form enumerates all the possible properties that exist
    and must have values specified for them in the 'yocto bsp create'
    command for the given 'karch'.  Example output for that command:

     $ yocto-bsp list i386 properties
         "machine": boolean,
          "kmachine": choice,
          "tunefile": choicelist,
          "smp": boolean,
          "xserver": choicelist
              ["xserver-choice": choice]
          "kfeatures": choicelist
              ["kfeature": choice]
           "touchscreen": boolean,
           "keyboard": boolean

    The third form enumerates all the possible values that exist and
    can be specified for any of the enumerable properties of the given
    'karch' in the 'yocto bsp create' command.  Example output for
    those properties:

     $ yocto-bsp list i386 property xserver
          xserver-vesa
          xserver-i915
          xserver-emgd

     $ yocto-bsp list i386 property kfeatures
          features/taskstats
          cfg/sound

     $ yocto-bsp list i386 property tunefile
          i386
              tune-atom
              tune-core2

     $ yocto-bsp list x86_64 property tunefile
          x86_64
              tune-x86_64
              tune-corei7
              tune-ivb

     $ yocto-bsp list powerpc property tunefile
          powerpc
              tune-ppc603e
              tune-ppce300c2
              tune-ppce500
              tune-ppce500mc
              tune-ppce500v2
              tune-ppce5500-32b
              tune-ppce5500-64b

     $ yocto-bsp list arm property tunefile
          arm
              tune-arm1136jf-s
              tune-arm920t
              tune-arm926ejs
              tune-arm9tdmi
              tune-armv7

     $ yocto-bsp list mips property tunefile
          mips
              tune-mips32
"""

##
# yocto-kernel help and usage strings
##

yocto_kernel_usage = """

 Modify and list Yocto BSP kernel features, config items, and patches.

 usage: yocto-kernel [--version] [--help] COMMAND [ARGS]

 The most commonly used 'yocto-kernel' commands are:
   feature list      List available Yocto KERNEL_FEATUREs
   feature define    Define a new Yocto KERNEL_FEATURE
   feature add       Add Yocto KERNEL_FEATUREs to a BSP
   feature rm        Remove Yocto KERNEL_FEATUREs from a BSP
   config list       List the modifiable set of bare kernel config options for a BSP
   config add        Add or modify bare kernel config options for a BSP
   config rm         Remove bare kernel config options from a BSP
   patch list        List the patches associated with a BSP
   patch add         Patch the Yocto kernel for a BSP
   patch rm          Remove patches from a BSP
   publish           Move local kernel config/patches to a git repo

 See 'yocto-kernel help COMMAND' for more information on a specific command.

"""


yocto_kernel_help_usage = """

 usage: yocto-kernel help <subcommand>

 This command displays detailed help for the specified subcommand.
"""


yocto_kernel_feature_list_usage = """

 List available Yocto KERNEL_FEATUREs

 usage: yocto-kernel feature list <bsp-name> [--used | -u]

 This command lists all the kernel features available to a BSP.
 This includes any features temporarily attached to the named BSP
 via the 'feature define' command and thus the reason this command
 takes bsp-name as a parameter.

 If the --used param is specified, only the KERNEL_FEATURES used by
 the BSP are listed.
"""


yocto_kernel_feature_list_help = """

NAME
    yocto-kernel-feature-list - List available Yocto KERNEL_FEATUREs

SYNOPSIS
    yocto-kernel feature list <bsp-name> --used

DESCRIPTION
    This command lists all the kernel features available to a BSP.
    This includes any features temporarily attached to the named BSP
    via the 'feature define' command and thus the reason this command
    takes bsp-name as a parameter.

    If the --used param is specified, only the KERNEL_FEATURES used by
    the BSP are listed.
"""


yocto_kernel_feature_define_usage = """

 Define a new Yocto KERNEL_FEATURE

 usage: yocto-kernel feature define <bsp-name> <feature-name>
    <feature-desc> [<CONFIG_XXX=x> ...] [--dirname <dirname>]
    [--policy <hw|non-hw>]

 This command defines a new kernel feature, resulting in the addition
 of two new files for feature xxx to the named BSP's SRC_URI.  If
 dirname is specified, the feature files will be named
 features_dirname_xxx.cfg and features_dirname_xxx.scc.  Otherwise,
 the features will be named cfg_xxx.cfg and cfg_xxx.scc.

 The policy stating whether the new feature is considered to be a
 hardware or a non-hardware feature can also be specified - if not
 specified, the default is non-hw.  A description of the new feature
 is also required; this will be added as a comment to the .scc file.
"""


yocto_kernel_feature_define_help = """

NAME
    yocto kernel feature define - Define a new Yocto KERNEL_FEATURE

SYNOPSIS
    yocto-kernel feature define <bsp-name> <feature-name> <feature-desc>
    [<CONFIG_XXX=x> ...] [--dirname <dirname>] [--policy <hw|non-hw>]

DESCRIPTION
    This command defines a new kernel feature, resulting in the
    addition of two new files for feature xxx to the named BSP's
    SRC_URI.  If dirname is specified, the feature files will be named
    features_dirname_xxx.cfg and features_dirname_xxx.scc.  Otherwise,
    the features will be named cfg_xxx.cfg and cfg_xxx.scc.  The idea
    behind the naming is that the names reflect the user's intent to
    have the feature migrated to either the kernel-cache/cfg or
    kernel-cache/features directory if/when the kernel portion of the
    BSP is migrated into the linux-yocto kernel repo.

    The policy stating whether the new feature is considered to be a
    hardware or a non-hardware feature can also be specified - if not
    specified, the default is non-hw.  A description of the new
    feature is also required; this will be added as a comment to the
    .scc file.

    NOTE: Although features are not BSP-specific, until the user has
    gone through the steps of migrating a feature to the linux-yocto
    repo, it needs to live somewhere accessible to the BSP metadata,
    which logically would be the kernel SRC_URI for the BSP using it.

    NOTE: It's up to the user to determine whether or not the config
    options for a feature being added make sense or not - this command
    does no sanity checking or verification of any kind to ensure that
    the config options contained in a kernel feature really make sense
    and will actually be set in in the final config.  For example, if
    a config option depends on other config options, it will be turned
    off by kconfig if the other options aren't set correctly.
"""


yocto_kernel_feature_add_usage = """

 Add Yocto KERNEL_FEATUREs to a BSP

 usage: yocto-kernel feature add <bsp-name> [<FEATURE> ...]

 This command adds one or more kernel features to a BSP.  The set of
 features available to be added by this command for a BSP can be found
 via the 'yocto-kernel feature list' command.  This command
 essentially adds a new machine-specific KERNEL_FEATURE_append to the
 linux-yocto .bbappend for the BSP.
"""


yocto_kernel_feature_add_help = """

NAME
    yocto-kernel-feature-add - Add Yocto KERNEL_FEATUREs to a BSP

SYNOPSIS
    yocto-kernel feature add <bsp-name> [<FEATURE> ...]

DESCRIPTION
    This command adds one or more kernel features to a BSP.  The set
    of features available to be added by this command for a BSP can be
    found via the 'yocto-kernel feature list' command.  This command
    essentially adds a new machine-specific KERNEL_FEATURE_append to
    the linux-yocto .bbappend for the BSP.
"""

yocto_kernel_feature_rm_usage = """

 Remove Yocto KERNEL_FEATUREs from a BSP

 usage: yocto-kernel feature rm <bsp-name> [<FEATURE> ...]

 This command removes one or more kernel features from a BSP.  The set
 of features available to be removed by this command for a BSP can be
 found via the 'yocto-kernel feature list' command, if the --used
 option to that command is specified.  This command essentially
 removes a machine-specific KERNEL_FEATURE from the linux-yocto
 .bbappend for the BSP.
"""


yocto_kernel_feature_rm_help = """

NAME
    yocto-kernel feature rm - Remove Yocto KERNEL_FEATUREs from a BSP

SYNOPSIS
    yocto-kernel feature rm <bsp-name> [<FEATURE> ...]

DESCRIPTION
    This command removes one or more kernel features from a BSP.  The
    set of features available to be removed by this command for a BSP
    can be found via the 'yocto-kernel feature list' command, if the
    --used option to that command is specified.  This command
    essentially removes a machine-specific KERNEL_FEATURE from the
    linux-yocto .bbappend for the BSP.
"""


yocto_kernel_config_list_usage = """

 List the modifiable set of bare kernel config options for a BSP

 usage: yocto-kernel config list <bsp-name>

 This command lists the 'modifiable' config items for a BSP i.e. the
 items which are eligible for modification or removal by other
 yocto-kernel commands.

 'modifiable' config items are the config items contained a BSP's
 foo.cfg base config.
"""


yocto_kernel_config_list_help = """

NAME
    yocto-kernel config list - List the modifiable set of bare kernel
    config options for a BSP

SYNOPSIS
    yocto-kernel config list <bsp-name>

DESCRIPTION
    This command lists the 'modifiable' config items for a BSP
    i.e. the items which are eligible for modification or removal by
    other yocto-kernel commands.
"""


yocto_kernel_config_add_usage = """

 Add or modify bare kernel config options for a BSP

 usage: yocto-kernel config add <bsp-name> [<CONFIG_XXX=x> ...]

 This command adds one or more CONFIG_XXX=x items to a BSP's foo.cfg
 base config.  If a config item is already present, the new value will
 simply overwrite the old value.
"""


yocto_kernel_config_add_help = """

NAME
    yocto-kernel config add - Add or modify bare kernel config options
    for a BSP

SYNOPSIS
    yocto-kernel config add <bsp-name> [<CONFIG_XXX=x> ...]

DESCRIPTION
    This command adds one or more CONFIG_XXX=x items to a BSP's
    foo.cfg base config.  If a config item is already present, the new
    value will simply overwrite the old value.

    NOTE: It's up to the user to determine whether or not the config
    options being added make sense or not - this command does no
    sanity checking or verification of any kind to ensure that a
    config option really makes sense and will actually be set in in
    the final config.  For example, if a config option depends on
    other config options, it will be turned off by kconfig if the
    other options aren't set correctly.
"""


yocto_kernel_config_rm_usage = """

 Remove bare kernel config options from a BSP

 usage: yocto-kernel config rm <bsp-name>

 This command removes (turns off) one or more CONFIG_XXX items from a
 BSP's foo.cfg base config.

 The set of config items available to be removed by this command for a
 BSP is listed and the user prompted for the specific items to remove.
"""


yocto_kernel_config_rm_help = """

NAME
    yocto-kernel config rm - Remove bare kernel config options from a
    BSP

SYNOPSIS
    yocto-kernel config rm <bsp-name>

DESCRIPTION
    This command removes (turns off) one or more CONFIG_XXX items from a
    BSP's foo.cfg base config.

    The set of config items available to be removed by this command
    for a BSP is listed and the user prompted for the specific items
    to remove.
"""


yocto_kernel_patch_list_usage = """

 List the patches associated with the kernel for a BSP

 usage: yocto-kernel patch list <bsp-name>

 This command lists the patches associated with a BSP.

 NOTE: this only applies to patches listed in the kernel recipe's SRC_URI.
"""


yocto_kernel_patch_list_help = """

NAME
    yocto-kernel patch list - List the patches associated with the kernel
    for a BSP

SYNOPSIS
    yocto-kernel patch list <bsp-name>

DESCRIPTION
    This command lists the patches associated with a BSP.

    NOTE: this only applies to patches listed in the kernel recipe's SRC_URI.
"""


yocto_kernel_patch_add_usage = """

 Patch the Yocto kernel for a specific BSP

 usage: yocto-kernel patch add <bsp-name> [<PATCH> ...]

 This command adds one or more patches to a BSP's machine branch.  The
 patch will be added to the BSP's linux-yocto kernel SRC_URI and will
 be guaranteed to be applied in the order specified.
"""


yocto_kernel_patch_add_help = """

NAME
    yocto-kernel patch add - Patch the Yocto kernel for a specific BSP

SYNOPSIS
    yocto-kernel patch add <bsp-name> [<PATCH> ...]

DESCRIPTION
    This command adds one or more patches to a BSP's machine branch.
    The patch will be added to the BSP's linux-yocto kernel SRC_URI
    and will be guaranteed to be applied in the order specified.

    NOTE: It's up to the user to determine whether or not the patches
    being added makes sense or not - this command does no sanity
    checking or verification of any kind to ensure that a patch can
    actually be applied to the BSP's kernel branch; it's assumed that
    the user has already done that.
"""


yocto_kernel_patch_rm_usage = """

 Remove a patch from the Yocto kernel for a specific BSP

 usage: yocto-kernel patch rm <bsp-name>

 This command removes one or more patches from a BSP's machine branch.
 The patch will be removed from the BSP's linux-yocto kernel SRC_URI
 and kernel SRC_URI dir.

 The set of patches available to be removed by this command for a BSP
 is listed and the user prompted for the specific patches to remove.
"""


yocto_kernel_patch_rm_help = """

NAME
    yocto-kernel patch rm - Remove a patch from the Yocto kernel for a specific BSP

SYNOPSIS
    yocto-kernel patch rm <bsp-name>

DESCRIPTION
    This command removes one or more patches from a BSP's machine branch.
    The patch will be removed from the BSP's linux-yocto kernel SRC_URI.

    The set of patches available to be removed by this command for a
    BSP is listed and the user prompted for the specific patches to
    remove.
"""


yocto_kernel_publish_usage = """

 Move local kernel config/patches to a git repo

 usage: yocto-kernel publish <bsp-name> <local linux-yocto repo>

 This command converts the kernel configuration changes, patches, and
 features collected in a BSP's linux-yocto SRC_URI into an equivalent
 set of commits in a local linux-yocto repo.  On success, the local
 files will named in the SRC_URI will be removed, and the linux-yocto
 .bbappend will be fixed up to point to the new repo.
"""


yocto_kernel_publish_help = """

NAME
    yocto-kernel publish - Move local kernel config/patches to a git repo

SYNOPSIS
    yocto-kernel publish <bsp-name> <local linux-yocto repo>

DESCRIPTION
    This command converts the kernel configuration changes, patches,
    and features collected in a BSP's linux-yocto SRC_URI into an
    equivalent set of commits in a local linux-yocto repo.  On
    success, the local files will named in the SRC_URI will be
    removed, and the linux-yocto .bbappend will be fixed up to point
    to the new repo.

    NOTE: The user is responsible for submitting the generated commits
    upstream and subsequently modifying the kernel .bbappend to
    use the upsteam kernel repo.
"""


##
# test code
##

test_bsp_properties = {
    'smp': 'yes',
    'touchscreen': 'yes',
    'keyboard': 'no',
    'xserver': 'yes',
    'xserver_choice': 'xserver-i915',
    'features': ['goodfeature', 'greatfeature'],
    'tunefile': 'tune-quark',
}


GCCMULTILIB = "--enable-multilib"

addtask gcc_multilib_setup after do_patch before do_configure

# following code modifies these definitions in the gcc config
#    MULTILIB_OPTIONS
#    MULTILIB_DIRNAMES
#    MULTILIB_OSDIRNAMES
#    GLIBC_DYNAMIC_LINKER32
#    GLIBC_DYNAMIC_LINKER64
#    GLIBC_DYNAMIC_LINKERX32
#    GLIBC_DYNAMIC_LINKERN32
#  For more information on use of these variables look at these files in the gcc source code
#    gcc/config/i386/t-linux64
#    gcc/config/i386/t-linux
#    gcc/config/mips/t-linux64
#    gcc/config/mips/t-linux
#    gcc/config/rs6000/t-linux64
#    gcc/config/i386/linux64.h
#    gcc/config/i386/linux.h
#    gcc/config/mips/linux64.h
#    gcc/config/rs6000/linux64.h
#    gcc/config/rs6000/linux.h
# Nitin Kamble 2012/02/13

python do_gcc_multilib_setup() {
    import re

    # do this only for target recipe
    if d.getVar('PN', True) != 'gcc':
        return

    srcdir = d.getVar('S', True)
    multilibs = d.getVar('MULTILIB_VARIANTS', True)
    target_arch = d.getVar('TARGET_ARCH', True)

    gcc_target_config_files = {     
        'x86_64'      : ['gcc/config/i386/t-linux64', 'gcc/config/i386/t-linux'],
        'i586'        : ['gcc/config/mips/t-linux'],
        'mips'        : ['gcc/config/mips/t-linux64', 'gcc/config/mips/t-linux'],
        'ppc'         : ['gcc/config/rs6000/t-linux64'] }

    gcc_header_config_files = {     
        'x86_64'      : ['gcc/config/i386/linux64.h'],
        'i586'        : ['gcc/config/mips/linux.h'],
        'mips'        : ['gcc/config/mips/linux64.h', 'gcc/config/mips/linux.h'],
        'ppc'         : ['gcc/config/rs6000/linux64.h', 'gcc/config/rs6000/linux.h'] }

    if target_arch not in gcc_target_config_files:
        bb.warn('gcc multilib setup is not supported for TARGET_ARCH=' + target_arch)
        return

    gcc_multilib_target_config_files = gcc_target_config_files[target_arch]
    gcc_multilib_header_config_files = gcc_header_config_files[target_arch]

    ml_list = ['DEFAULTTUNE']
    if multilibs != '':
        for ml in multilibs.split(' '):
            ml_list.append('DEFAULTTUNE_virtclass-multilib-' + ml)

    libdir32 = 'SYSTEMLIBS_DIR'
    libdir64 = 'SYSTEMLIBS_DIR'
    libdirx32 = 'SYSTEMLIBS_DIR'
    libdirn32 = 'SYSTEMLIBS_DIR'

    multilib_options = []
    multilib_dirnames = []
    multilib_osdirnames = []

    for ml in ml_list:
        tune = d.getVar(ml, True)
	tune_parameters = get_tune_parameters(tune, d)
	for a, b in tune_parameters.iteritems():
		bb.warn(a + ': ' + b)

        tune_baselib = tune_parameters['baselib']

        if tune_baselib == 'lib64':
            libdir64 = tune_baselib
        elif tune_baselib == 'libx32':
            libdirx32 = tune_baselib
        elif tune_baselib == 'lib32':
            libdirn32 = tune_baselib
        elif tune_baselib == 'lib':
            libdir32 = tune_baselib
        else:
            bb.error('Unknown libdir (%s) of the tune : %s' % (tune_baselib, tune))

        # take out '-' in parameters
        multilib_options.append(re.sub(r' +\-+', ' ', re.sub(r'^ *\-+', '', tune_parameters['ccargs'])))
        if tune_baselib == 'lib':
            multilib_dirnames.append('32')  # /lib => 32bit lib
        else:
            multilib_dirnames.append(tune_baselib.replace('lib', ''))
        multilib_osdirnames.append('../' + tune_baselib)
    
    # go over t-linux64 kind target files
    for ml_conf_file in gcc_multilib_target_config_files:
        with open(srcdir + '/' + ml_conf_file, 'r') as f:
            filelines = f.read()
            f.close()

            # recreate multilib configuration variables

            filelines = re.sub(r'^\s*MULTILIB_OPTIONS\s*=.*$',
                'MULTILIB_OPTIONS = ' + '/'.join(multilib_options),
                filelines, flags=re.MULTILINE)

            filelines = re.sub(r'^\s*MULTILIB_DIRNAMES\s*=.*$',
                'MULTILIB_DIRNAMES = ' + ' '.join(multilib_dirnames),
                filelines, flags=re.MULTILINE)

            filelines = re.sub(r'^\s*MULTILIB_OSDIRNAMES\s*=.*$',
                'MULTILIB_OSDIRNAMES = ' + ' '.join(multilib_osdirnames),
                filelines, flags=re.MULTILINE)
    
            with open(srcdir + '/' + ml_conf_file, 'w') as f:
                f.write(filelines)
                f.close()
            with open('/tmp/ml.out', 'w') as f:
                f.write(filelines)
                f.close()

    # go over linux64.h kind header files
    for ml_conf_file in gcc_multilib_header_config_files:
        with open(srcdir + '/' + ml_conf_file, 'r') as f:
            filelines = f.read()
            f.close()

            # replace lines like
            # #define GLIBC_DYNAMIC_LINKER32 SYSTEMLIBS_DIR "ld-linux.so.2"
            # by
            # #define GLIBC_DYNAMIC_LINKER32 "/lib/" "ld-linux.so.2"
            # this is needed to put the correct dynamic loader path in the generated binaries

            filelines = re.sub(r'^(#define\s*GLIBC_DYNAMIC_LINKER32\s*)(SYSTEMLIBS_DIR)(\s*\".*\")$',
                r'\1"/' + libdir32 + r'/"\3',
                filelines, flags=re.MULTILINE)

            filelines = re.sub(r'^(#define\s*GLIBC_DYNAMIC_LINKER64\s*)(SYSTEMLIBS_DIR)(\s*\".*\")$',
                r'\1"/' + libdir64 + r'/"\3',
                filelines, flags=re.MULTILINE)

            filelines = re.sub(r'^(#define\s*GLIBC_DYNAMIC_LINKERX32\s*)(SYSTEMLIBS_DIR)(\s*\".*\")$',
                r'\1"/' + libdirx32 + r'/"\3',
                filelines, flags=re.MULTILINE)

            filelines = re.sub(r'^(#define\s*GLIBC_DYNAMIC_LINKERN32\s*)(SYSTEMLIBS_DIR)(\s*\".*\")$',
                r'\1"/' + libdirn32 + r'/"\3',
                filelines, flags=re.MULTILINE)

            with open(srcdir + '/' + ml_conf_file, 'w') as f:
                f.write(filelines)
                f.close()
}

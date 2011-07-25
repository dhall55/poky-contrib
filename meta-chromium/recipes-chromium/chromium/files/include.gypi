{
  'variables': {

    # Configure for ia32 compilation
    'target_arch': 'ia32',
    'ia32': 1,

    # disable -Werror
    'werror': '',

    # Disable native client (Google's settings)
    'disable_nacl': 1,

    # V8 config (Google's settings)
    'v8_use_snapshot': 'false',

    # make sure the build will not fail
    'use_system_ffmpeg' : '0',

    # Needed for ia32 compilation? (build fails otherwise)
    'linux_use_tcmalloc': 0,

    # Change to your rootfs path
    'sysroot': '__PATH__TO_BE_REPLACED__',

    #'ia32_thumb': 1,
  }
}

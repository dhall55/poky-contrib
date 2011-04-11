require glib.inc

PE = "1"
PR = "r0"

SRC_URI = "http://ftp.gnome.org/pub/GNOME/sources/glib/2.28/glib-${PV}.tar.bz2 \
           file://configure-libtool.patch \
           file://60_wait-longer-for-threads-to-die.patch \
           file://g_once_init_enter.patch \
          "

# This should not be necessary; however there was some kind of mismatch in pcre.h
# even though diff only reports that the copyright date changed (which is before line 11)
LIC_FILES_CHKSUM = "file://COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://glib/glib.h;startline=4;endline=17;md5=a4332fe58b076f29d07c9c066d2967b6 \
                    file://gmodule/COPYING;md5=3bf50002aefd002f49e7bb854063f7e7 \
                    file://gmodule/gmodule.h;startline=4;endline=17;md5=76ab161b37202cd004073c42fac276ed \
                    file://glib/pcre/COPYING;md5=266ebc3ff74ee9ce6fad65577667c0f4 \
                    file://glib/pcre/pcre.h;startline=11;endline=35;md5=ce867cf87ebbd2bb55e980d90328390d \
                    file://docs/reference/COPYING;md5=f51a5100c17af6bae00735cd791e1fcc"

SRC_URI[md5sum] = "ddf80a060ec9039ad40452ba3ca2311b"
SRC_URI[sha256sum] = "8eb4b56b228c6d0bf5021dd23db5b0084d80cc6d8d89d7863073c2da575ec22a"

SRC_URI_append_virtclass-native = " file://glib-gettextize-dir.patch"
BBCLASSEXTEND = "native"

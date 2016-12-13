#! /usr/bin/python

# Python ctypes bindings for VLC
#
# Copyright (C) 2009-2012 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <contact at olivieraubert.net>
#          Jean Brouwers <MrJean1 at gmail.com>
#          Geoff Salmon <geoff.salmon at gmail.com>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301 USA

"""This module provides bindings for the LibVLC public API, see
U{http://wiki.videolan.org/LibVLC}.

You can find the documentation and a README file with some examples
at U{http://www.advene.org/download/python-ctypes/}.

Basically, the most important class is L{Instance}, which is used
to create a libvlc instance.  From this instance, you then create
L{MediaPlayer} and L{MediaListPlayer} instances.

Alternatively, you may create instances of the L{MediaPlayer} and
L{MediaListPlayer} class directly and an instance of L{Instance}
will be implicitly created.  The latter can be obtained using the
C{get_instance} method of L{MediaPlayer} and L{MediaListPlayer}.
"""


from ctypes.util import find_library
import os
import sys

# Used by EventManager in override.py
#from inspect import getargspec

__version__ = "N/A"
build_date  = "Mon Feb  1 16:15:29 2016"

# The libvlc doc states that filenames are expected to be in UTF8, do
# not rely on sys.getfilesystemencoding() which will be confused,
# esp. on windows.
DEFAULT_ENCODING = 'utf-8'

if sys.version_info[0] > 2:
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
    PYTHON3 = True
    def str_to_bytes(s):
        """Translate string or bytes to bytes.
        """
        if isinstance(s, str):
            return bytes(s, DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to string.
        """
        if isinstance(b, bytes):
            return b.decode(DEFAULT_ENCODING)
        else:
            return b
else:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
    PYTHON3 = False
    def str_to_bytes(s):
        """Translate string or bytes to bytes.
        """
        if isinstance(s, unicode):
            return s.encode(DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to unicode string.
        """
        if isinstance(b, str):
            return unicode(b, DEFAULT_ENCODING)
        else:
            return b

# Internal guard to prevent internal classes to be directly
# instanciated.
#_internal_guard = object()

def find_lib():
    plugin_path = None

    if sys.platform.startswith('win'):
        p = find_library('libvlc.dll')
        if p is None:
            try:  # some registry settings
                # leaner than win32api, win32con
                if PYTHON3:
                    import winreg as w
                else:
                    import _winreg as w
                for r in w.HKEY_LOCAL_MACHINE, w.HKEY_CURRENT_USER:
                    try:
                        r = w.OpenKey(r, 'Software\\VideoLAN\\VLC')
                        plugin_path, _ = w.QueryValueEx(r, 'InstallDir')
                        w.CloseKey(r)
                        break
                    except w.error:
                        pass
            except ImportError:  # no PyWin32
                pass
            if plugin_path is None:
                 # try some standard locations.
                for p in ('Program Files\\VideoLan\\', 'VideoLan\\',
                          'Program Files\\',           ''):
                    p = 'C:\\' + p + 'VLC\\libvlc.dll'
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                
                 # restore cwd after dll has been loaded
                os.chdir(p)
        else:
            plugin_path = os.path.dirname(p)

    else:
        raise NotImplementedError('%s: %s not supported' % (sys.argv[0], sys.platform))

    return plugin_path

# plugin_path used on win32 and MacOS in override.py
vlc_path  = find_lib()

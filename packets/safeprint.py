#   Credit:     http://stackoverflow.com/a/10667978

from __future__ import print_function
import sys

def safeprint(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            print(s.encode('utf8').decode(sys.stdout.encoding))
        else:
            print(s.encode('utf8'))

#   safeprint(u"\N{EM DASH}")

#!/usr/bin/env python

'''

Credit: Derrived from http://joejulian.name/blog/quick-and-dirty-python-script-to-check-the-dirty-status-of-files-in-a-glusterfs-brick/

__author__="David Busby <d.busby@saiweb.co.uk>"
__copyright__="David Busby && Psycle Interactive Ltd"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

import os
import sys
import stat

class opts:
    slen = 0

def _err(txt):
    sys.stderr.write("[\033[31mERROR\033[0m] "+txt+"\n")

try:
    import xattr
except ImportError:
   _err("Could not import xattr, this is required to continue, try: easy_install xattr")

def progress(str):
    '''
        todo: there has to be a better way of doing this rather that overwriting the string at every given point
    '''
    while len(str) < opts.slen:
        str = '%s ' % str    
        opts.slen = len(str)
        sys.stdout.write(str + '\r')
        sys.stdout.flush()


def usage():
    print("Usage: " + sys.argv[0] + " /path/to/brick/dir")
    print("Note: This is not a nfs / glusterfs mount point, this is the file system native brick folder")
    sys.exit(2)

def main():
    
    try:
        brick = sys.argv[1]
    except IndexError:
        _err('No directory specified')
        usage()

    if not os.path.isdir(brick):
        _err(brick + " is not a valid directory")
    else:
        files = []
        cFiles = 0
        for root, dirs, files in os.walk(brick):
            for fname in files:
                file = os.path.join(root,fname)
                if stat.S_ISREG(file):
                    progress('Please wait, while gathering file list (%d)'%cFiles)
                    cFiles += 1
                

            
    

if __name__ == "__main__":
    main()

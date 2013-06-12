import sys
import os
import re
reAFR = re.compile('trusted\.afr\..*')
try:
    import xattr
except ImportError:
    print("Could not import module xattr this is required!")
    sys.exit(1)

'''

This python is designed to aid resolution of a split-brain scenario with Gluster.

This assumes replicate volumes are in use, and that you have a single "good" copy of your data.

This script will walk the filesystem of the "bad" data removing all the extended attributes associated with gluster, you can then rsync good -> bad overriting / updating any missing files, and return gluster to a working state on the "bad" brick.

__author__="David Busby <david.busby@psycle.com>"
__copyright__="David Busby && Psycle Interactive Ltd"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

def banner():
    print("----\n\nWARNING: This script will walk the provided path removing all trusted.gfid and truster.afr.* xattr's")
    print("Make sure glusterd is stopped and all filesystems unmounted")
    print("You MUST walk the back-end filesystem NOT the mountpoint")
    print("Whilst gluster MAY resync the data when restarted, I have found using rsync to first bring the 'bad' brick in sync first to be the most effective i.e. rsync -gioprtv")
    print("You break it you fix it, this script is not intended as a FIRE and forget solution!\n\n----")

def main():
    banner()
    p = raw_input("Please provide the BAD back-end file system folder NOT the mountpoint: ")
    while not os.path.isdir(p):
       p = raw_input("Invalid input %s is not a directory, please enter the correct path: "%p)
    a = raw_input("Last chance to back out, are you sure you want me to walk %s and remove all gluster xattrs I find? (y/n): "%p)
    while a.lower() not in ('y','n'):
        a = raw_input("Invalid input %s, please specify y or n: "%a)
    if a.lower() == 'n':
        sys.exit(0)
    '''
        Now we have a valid path, and user concent
    '''
    
    for root, dirs, files in os.walk(p):
        '''
            At the time of writing gluster only sets xarrts on directories
        '''
        xattrs = xattr.listxattr(root)
        if len(xattrs) > 0:
            if 'trusted.gfid' in xattrs:
                print("Found trusted.gfid set on %s"%root)
                xattr.removexattr(root,'trusted.gfid')
            for attr in xattrs:
                if reAFR.search(attr):
                    print("Found truster.afr.* set on %s"%root)
                    xattr.removexattr(root,attr)

       
if __name__ == '__main__':
    main()     

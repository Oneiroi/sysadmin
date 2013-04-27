import sys
import os
import re
from base64 import b64encode
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

def main():
    p = sys.argv[1] 
    while not os.path.isdir(p):
       p = raw_input("Invalid input %s is not a directory, please enter the correct path: "%p)
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
                print('%s trusted.gifd: %s' % (root,b64encode(xattr.getxattr(root,'trusted.gfid'))))
            for attr in xattrs:
                if reAFR.search(attr):
                    print('%s %s: %s'%(root,attr,b64encode(xattr.getxattr(root,attr))))
       
if __name__ == '__main__':
    main()     

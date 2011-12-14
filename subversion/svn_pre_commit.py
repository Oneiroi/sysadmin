#!/usr/bin/env python
"""
    Author: David Busby (http://saiweb.co.uk)
    Program: force message
    Description: Python subversion call back forces committer to specify a log message longer thank 10 chars
    Copyright: David Busby, Psycle Interactive Ltd 2009 All rights reserved.
    License: http://creativecommons.org/licenses/by-sa/2.0/uk/
"""

import sys, os, string
from fnmatch import fnmatch

def main(repo,txn):
    #enforce a comment
    cmd = '/usr/bin/svnlook log -t "%s" "%s"' % (txn,repo)
    str = os.popen(cmd, 'r').readline().rstrip('\n')
    
    if(len(str) <= 10):
        sys.stderr.write('Log message is too short, your commit has been refused\n')
        sys.exit(1)
    #ban certain extentions
    banned = ['*.tgz','*.tar*','*.zip','*.gz','*.bz*','*.pyc','*.so*','*.o','*.swp','*.exe','*.bak','*.old','*.dll','*.rar','*.obj','*.out','thumbs.db']
    cmd = '/usr/bin/svnlook changed -t "%s" "%s"' % (txn,repo)
    str = os.popen(cmd, 'r').readline().rstrip('\n')
    for line in str.split('\n'):
	for ban in banned:
		if fnmatch(line.lower(),ban):
			sys.stderr.write('Rejected commit as it contains a banned file extension %s\n'%ban)
			sys.exit(1)
	
    sys.exit(0)
    
if __name__ == '__main__':
    
    if(len(sys.argv) < 3):
        sys.stderr.write('Usage: %s /path/to/repo txn \n' % (sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1], sys.argv[2])

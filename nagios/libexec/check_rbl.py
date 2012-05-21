#!/usr/bin/env python
#  RBL list checker
#  Created by David Busby on 18/05/2009.
#
#  Copyright (c) 2009 Psycle, David Busby

"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

import sys, string, socket, getopt
#global vars
TAG="RBL_LOOKUP"

def check(ip, rbl_domain):
    tmp = string.split(ip,".")
    tmp.reverse()

    lookup = string.join(tmp,".")+"."+rbl_domain
    try:
        addr = socket.gethostbyname(lookup)
    except socket.error:
        addr=False
    
    return addr

def usage():
    print "Usage: ",sys.argv[0]," [-s rbl.fqdn.tld][-i aaa.bbb.ccc.ddd]"
    print "-s RBL FQDN"
    print "-i ip address to lookup"
    sys.exit(0)
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:i:", ["help", "output="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    
    srv = ''
    ip = ''
    for o, a in opts:
        if o in ("-h", "--help"):
           usage()
        elif o == "-s":
           srv = a
        elif o == "-i":
            ip = a
    
    if len(srv) > 0 and len(ip) > 0:
        res = check(ip, srv)
        if res == False:
            stat = "%s Not listed at %s" % (ip, srv)
            ok(stat)
        else:
            stat = "%s listed at %s return code: %s" % (ip, srv, res)
            critical(stat);
            
def ok(stat):
    print TAG,"OK -",stat
    sys.exit(0)
    
def warn(stat):
    print TAG,"WARN -",stat
    sys.exit(1)
    
def critical(stat):
    print TAG,"CRITICAL -",stat
    sys.exit(2);


if __name__ == "__main__":
    main()
    

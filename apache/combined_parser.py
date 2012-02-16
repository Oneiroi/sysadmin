import re
import sys
import os
import getopt
'''
__author__="David Busby"
__copyright__="David Busby <d.busby@saiweb.co.uk>"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
'''

try:
    import hashlib
except:
    print 'Your python version does not include hashlib, importing md5 instead'
    import md5 as hashlib
try:
    import multiprocessing
except:
    print 'This script requires the multiprocessing lib to function, included in python 2.6+ or available from pypi for 2.5'
    sys.exit(1)

def parse(line):
    #dat = re.split('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s-\s[^\]]+\]\s"(.*)"\s([0-9]+)\s(-|[0-9]+)', line)
    dat = re.split('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)?[, ]+?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+|-)\s-\s[^\]]+\]\s"(.*)"\s([0-9]+)\s(-|[0-9]+)', line)
    ips = {}
    bytes = 0
    return dat

    
def usage():
    print sys.argv[0],'-f /path/to/combined.log -t Thread count (default: 1)'

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],'f:t:',[])
    except getopt.GetoptError, e:
        print e
        usage()
        sys.exit(2)

    lFile = ''
    threads = 1
    for o,a in opts:
        if o == '-f':
            if os.path.isfile(a):
                lFile = a
            else:
                print '404',a
                sys.exit(1)
        elif o == '-t':
            threads = int(a)
        else:
            assert False, 'UNsupported option %s %s' % (o,a)

    p = multiprocessing.Pool(processes=threads)
    
    lines = open(lFile,'r').readlines()
    data = p.map(parse,lines)
    http_codes = {}
    for i in  data:
        try:
            http_codes[i[4]] += 1
        except:
            http_codes[i[4]] = 1
    print http_codes

if __name__ == '__main__':
    main()

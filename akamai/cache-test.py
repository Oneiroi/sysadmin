import os
import sys
import httplib
from time import time,sleep,strftime,gmtime
from urlparse import urljoin, urlsplit
from socket import gethostbyname
from binascii import crc32


'''
    This utility will request the same url every 1 second, I suggest you have this script return a simple timestamp,
    this can be used to test Akamai caching is working as expect i.e. if you send a max-age=300 header, and you are returning a timestamp you would expect the output to be 5 minutes apart.


    __author__="David Busby"
    __copyright__="David Busby & Psycle Interactive Ltd"
    __license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
'''

def main():
    u = urlsplit(sys.argv[1])
    lr = ''
    print '--- Script will now check every 1s and print out when content changes'
    while 1:
        ip = gethostbyname(u.netloc)
        c = httplib.HTTPConnection(ip,80)
        c.request('GET',u.path,{},{'Host':u.netloc})
        r = c.getresponse()
        d = r.read()
        crc = crc32(d)
        if crc != lr:
            print ('[%s]' % strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())),ip,'-',d
            lr = crc
        sleep(1)

if __name__ == '__main__':
    main()

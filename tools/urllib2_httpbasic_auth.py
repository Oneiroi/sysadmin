#!/usr/bin/env python
"""
    Author: David Busby (http://saiweb.co.uk)
    Program: Python HTTP Basic Auth Exa
    Copyright: David Busby 2009. All rights reserved.
    License: http://creativecommons.org/licenses/by-sa/2.0/uk/
"""

import urllib2, base64

""" URL List """
urls = {
               0:{"url":"www.saiweb.co.uk/some/fictional/auth/area","user":"someuser","pass":"somepass"}
}

def main():
   ulen = len(urls)
   for i in range(0,ulen):
       url = "http://%s" % (urls[i]["url"])
       req = urllib2.Request(url)
       try:
           res = urllib2.urlopen(req)
           headers = res.info().headers
           data = res.read()
       except IOError, e:
            if hasattr(e, 'reason'):
                err = "%s ERROR(%s)" % (urls[i]["url"],e.reason)
                print err
            elif hasattr(e, 'code'):
                if e.code != 401:
                    err = "%s ERROR(%s)" % (urls[i]["url"],e.code)
                    print err
                #401 = auth required error
                elif e.code == 401:
                    base64string = base64.encodestring('%s:%s' % (urls[i]["user"], urls[i]["pass"]))[:-1]
                    authheader =  "Basic %s" % base64string
                    req.add_header("Authorization", authheader)
                    try:
                        res = urllib2.urlopen(req)
                        headers = res.info().headers
                        data = res.read()
                    except IOError, e:
                        if hasattr(e, 'reason'):
                            err = "%s:%s@%s ERROR(%s)" % (urls[i]["user"],urls[i]["pass"],urls[i]["url"],e.reason)
                            print err
                        elif hasattr(e, 'code'):
                            err = "%s:%s@%s ERROR(%s)" % (urls[i]["user"],urls[i]["pass"],urls[i]["url"],e.code)
                            print err
                    else:
                        err = "%s query complete" % (urls[i]["url"])
                        print err
       else:
            err = "%s query complete" % (urls[i]["url"])
            print err
                        
if __name__ == "__main__":
    main()
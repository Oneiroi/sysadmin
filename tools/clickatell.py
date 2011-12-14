#!/usr/bin/env python
"""
    Author: David Busby (http://saiweb.co.uk)
    Program: Clickatell
    Description: Script for sending SMS via clicaktell API
    Copyright: David Busby 2009. All rights reserved.
    License: http://creativecommons.org/licenses/by-sa/2.0/uk/
"""

import os,sys,urllib2,urllib,getopt

def usage():
    print "Usage: ",sys.argv[0]," [-u username][-p password][-a api id][-s your sms message][-n number]"
    sys.exit(1)
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:a:s:n:", ["help", "output="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    
    base_url = 'http://api.clickatell.com'
    
    usr = ''
    pwd = ''
    api_id = ''
    sms = ''
    number = ''
    
    for o, a in opts:
        if o in ("-h", "--help"):
           usage()
        elif o == "-u":
            usr = a
        elif o == "-p":
            pwd = a
        elif o == '-a':
            api_id = a
        elif o == '-s':
            sms = a
        elif o == '-n':
            number = a
    
    if(len(usr) == 0 or len(pwd) == 0 or len(api_id) == 0 or len(sms) == 0):
        usage()
        
    url = '%s/http/auth?user=%s&password=%s&api_id=%s' % (base_url,usr,pwd,api_id)
    req = urllib2.Request(url)
    
    try:
       res = urllib2.urlopen(req)
       headers = res.info().headers
       data = res.read()
    except IOError, e:
        if hasattr(e, 'reason'):
            err = "%s ERROR(%s)" % (url,e.reason)
            print err
            sys.exit(1)
        elif hasattr(e, 'code'):
            err = "%s ERROR(%s)" % (url,e.code)
            print err
            sys.exit(1)
            
    if data.split(':')[0] == 'OK':
        url = '%s/http/sendmsg?session_id=%s&to=%s&text=%s' % (base_url,data.split(':')[1].strip(),number,urllib.quote_plus(sms))
        req = urllib2.Request(url)
        try:
           res = urllib2.urlopen(req)
           headers = res.info().headers
           data = res.read()
        except IOError, e:
            if hasattr(e, 'reason'):
                err = "%s ERROR(%s)" % (url,e.reason)
                print err
                sys.exit(1)
            elif hasattr(e, 'code'):
                err = "%s ERROR(%s)" % (url,e.code)
                print err
                sys.exit(1)
        if data.split(':')[0] == 'ERR':
            print 'sms send FAILED'
            sys.exit(1)
    else:
        print 'Auth failed'
        print data
        
        
if __name__ == "__main__":
    main()
    
            
    




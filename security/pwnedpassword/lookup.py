#/usr/bin/env python 
from hashlib import sha1
from getpass import getpass
from requests import get

def main():
    print "This script will check your password against pwnedpasswords.com"
    print "This uses the k-Anonymity model, meaning we only lookup the first 5 chars of the sha1 digest of your password"
    print "Your password is never sent to pwnedpasswords this way"
    print
    passHash = sha1(getpass("Please provide the password to check: ")).hexdigest().upper()
    req  = get("https://api.pwnedpasswords.com/range/%s" % passHash[:5])
    if req:
        #pwnedpasswords API returns the hash suffice with count, with passHash[:5] being the hash prefix
        for line in req.text.split('\n'):
            if passHash[:5] + line.split(':')[0] == passHash:
                #We have a match, print this out
                print 
                print "[WARNING] Your password was noted on pwnedpasswords %s times" % line.split(':')[1]
                break
    #Clean up (Just to err on the side of paranoia)
    del passHash

if __name__ == '__main__':
    main()

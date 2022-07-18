#/usr/bin/env python 
from hashlib import sha1
from getpass import getpass
from requests import get

def main():
    print("This script will check your password against pwnedpasswords.com")
    print("This uses the k-Anonymity model, meaning we only lookup the first 5 chars of the sha1 digest of your password")
    print("Your password is never sent to pwnedpasswords this way")
    passHash = sha1(getpass("Please provide the password to check: ").encode("utf-8")).hexdigest().upper()
    req  = get("https://api.pwnedpasswords.com/range/%s" % passHash[:5])
    if req:
        #pwnedpasswords API returns the hash suffix:count, with passHash[:5] being the hash prefix
        #So the returned line will be passHash:count _IF_ there is a match
        for line in req.text.split('\n'):
            if passHash[:5] + line.split(':')[0] == passHash:
                #We have a match, print this out
                print ("[WARN] Your password was noted on pwnedpasswords %s times" % line.split(':')[1].strip())
                return
    #Clean up (Just to err on the side of paranoia)
    del passHash
    #_IF_ we are here, we can assume that there has been no matches
    print("[INFO] Good news, I could not find a match on api.pwnedpasswords.com, this does not count as endorsement for this password however")

if __name__ == '__main__':
    main()

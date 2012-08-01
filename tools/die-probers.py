#!/usr/bin/env/python

#
# Very quick n dirty script to halt probes in their tracks
# By D.Busby
# Note this is a script that was never completed, I suggest simply taking the regex pattern and using it wihin fail2ban to achieve the same results.

import re,os

from time import strftime,gmtime

LOGFILE='/var/log/die-probers.log'
ACCESSFILE='/var/log/httpd/access_log'
BANCMD='iptables -A INPUT -p tcp --dport 80 -s %s -j DROP -m comment --comment "%s"'
exclusions=[]
exclusions.append('aaa.bbb.ccc.ddd')

def log(str):
    str = '[%s] %s\n' %((strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())),str)
    f = file(LOGFILE, 'a+')
    f.write(str)
    f.close()

BANS=[]
def _getbans():
	log('_getbans')
	bans = os.popen("iptables --list -n | grep 'DROP' | awk '{print $4}'")
	for ban in bans.readlines():
		BANS.append(ban.rstrip("\n"))			

def _setban(ip,count):
	if ip not in BANS:
		if ip not in exclusions:
			str = BANCMD % (ip,'%s Banned via die-probers.py after %s attempts' % (strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),count))
			os.system(str)	
			log('%s not in known bans, BANNED' % ip)
		else:
			log('%s should be banned, however is in exclusions' % ip)
	else:
		log('%s is allready known, skipping' % ip)	
def startup():
	log('startup')
	_getbans()
	offenders = {}
	for line in open(ACCESSFILE,'r'):
		dat = re.split('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s-\s[^\]]+\]\s"(.*)"\s([0-9]+)\s(-|[0-9]+)',line)
		#-------------------------------------------------------- 1 = ip
                #-------------------------------------------------------- 2 = url
                #-------------------------------------------------------- 3 = http code
                #-------------------------------------------------------- 4 = bytes
		try:
			# checks for potential prober http response
			if int(dat[3]) in (302,403,404,500):
				#now do the lengthy regex match
				m=re.match('^GET\s//?(phpmy|admin|manage|sql|web|proxy|wantsfly|rc|round|mail|wm|bin|rms|mss).*$',dat[2])
				if m != None:
					log('%s got code %s and matched filter %s, full request %s' % (dat[1],dat[3],m.group(1),dat[2]))
					#we have a match record the results
					try:
						offenders[dat[1]]+=1
					except:
						offenders[dat[1]]=1
		except:
			continue
	banlist = offenders.items()
	banlist.sort(key=lambda (k,v): (v,k), reverse=True)
	for ban in banlist:
		log('%s matched %s lines during startup' % (ban[0],ban[1]))
		_setban(ban[0],ban[1])
if __name__ == '__main__':
	startup()	

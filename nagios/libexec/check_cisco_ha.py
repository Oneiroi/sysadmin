#!/usr/bin/env python

"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

import os,sys,getopt,re
TAG='CISCO_HA_CHECK'
# OK function used to return exit code 0 for nagios along with status message
# @var string stat status message
def ok(stat):
    print TAG,"OK -",stat
    sys.exit(0)
# WARN function used to return exit code 1 for nagios along with status message
# @var string stat status message
def warn(stat):
    print TAG,"WARN -",stat
    sys.exit(1)
#CRITICAL function used to return exit code 2 for nagios alonf with status message
# @var string stat status message
def critical(stat):
    print TAG,"CRITICAL -",stat
    sys.exit(2)

def usage():
        print sys.argv[0],' -s <aaa.bbb.ccc.ddd> -c public - <JMX....>'
	print ' -h / --help display this dialogue'
	print ' -s ipaddress to query'
	print ' -c snmp community '
	print ' -n serial number expected'
	print ' -i sid'
        sys.exit()

def main():
        #import required mods
        try:
                import netsnmp
        except ImportError, e:
                critical('Failed to load netsnmp, this module is required, you will need to install net-snmp >= 5.4.2.1 and compile the python bindings')

        opts, args = getopt.getopt(sys.argv[1:],"hs:c:n:i:",["help","output="])
	
	host = ''
	community = ''
	fwA = ''
        sid = ''
	for o, a in opts:
                if o in ('-h', '--help'):
                        usage()
                elif o == '-s':
                	host = a
                elif o == '-c':
                        community = a
		elif o == '-n':
			fwA = a
		elif o == '-i':
			sid = a
		

	if len(host) == 0 or len(community) == 0:
		usage()
		sys.exit(1)


	#ucd_oid = 'SNMPv2-SMI::mib-2'	
	ucd_oid = '.1.3.6.1.2.1' #SNMPv2-SMI::mib-2
	data_oids = { 
		'serial':'.47.1.1.1.1.11.1'	
	}

	#Time to get the data
	results = {} 
	oid = '%s%s' % (ucd_oid,data_oids['serial'])
	oid = netsnmp.Varbind(oid)
	result = netsnmp.snmpget(      oid,
                                        Version = 2,
                                        DestHost = "%s" % host,
                                        Community = "%s" % community)
	
	results.update({'serial':result})
	
	if fwA == results['serial'][0]:
		ok('expected %s running on %s (expected %s SID %s)'%(results['serial'][0],host,fwA,sid))
	else:
		warn('unexpected %s running on %s (expected %s SID %s)'%(results['serial'][0],host,fwA,sid))
if __name__ == '__main__':
        main()



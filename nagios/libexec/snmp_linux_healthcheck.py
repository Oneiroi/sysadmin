#!/usr/bin/env python

#
# Linux SNMP memory check, with PERF data
# Created by David Busby
# Copyright (c) 2010 Psycle Interactive Ltd, David Busby
#
#

"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

import os,sys,getopt,re
TAG='LINUX_SNMP_HEALTH_CHECK'
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
        print sys.argv[0],' -s <aaa.bbb.ccc.ddd> -c public -f 35 -g 10'
	print ' -h / --help display this dialogue'
	print ' -s ipaddress of server'
	print ' -c snmp community '
	print ' -f free memory percentage below which to warn'
	print ' -g free memory percentage below which to critical'
        sys.exit()

def main():
        #import required mods
        try:
                import netsnmp
        except ImportError, e:
                critical('Failed to load netsnmp, this module is required, you will need to install net-snmp >= 5.4.2.1 and compile the python bindings')

        opts, args = getopt.getopt(sys.argv[1:],"hs:c:f:g:",["help","output="])
	
	host = ''
	community = ''
	wFree = 20 
	cFree = 10
	wLoad = 5
	cLoad = 10
        for o, a in opts:
                if o in ('-h', '--help'):
                        usage()
                elif o == '-s':
                	host = a
                elif o == '-c':
                        community = a
		elif o == '-f':
			wFree = int(a)
		elif o == '-g':
			cFree = int(a)
		

	if len(host) == 0 or len(community) == 0:
		usage()
		sys.exit(1)


	ucd_oid = '.1.3.6.1.4.1.2021'
	data_oids = { 
				'load':'.10.1.3',
				'memTotalSwap':'.4.3',
				'memAvailSwap':'.4.4',
				'memInstalled':'.4.5',
				'memUsed':'.4.6',
				'memTotalFree':'.4.11',
				'memShared':'.4.13',
				'memBuffer':'.4.14',
				'memCached':'.4.15',
				}
	
	#Time to get the data
	results  = {}
	for item in data_oids:
		oid = '%s%s' % (ucd_oid,data_oids[item])
		oid = netsnmp.Varbind(oid)
		result = netsnmp.snmpwalk(      oid,
                                        Version = 2,
                                        DestHost = "%s" % host,
                                        Community = "%s" % community)
		results.update({item:result})
	#memTotalFree includes swap, we are looking to get REAL memory usage	
	memFree=int(results['memTotalFree'][0]) - int(results['memTotalSwap'][0]) + int(results['memBuffer'][0]) + int(results['memCached'][0])
	rawFree=int(results['memTotalFree'][0])
	memTotal=int(results['memInstalled'][0])
	buffers=int(results['memBuffer'][0])
	shared=int(results['memShared'][0])
	cached=int(results['memCached'][0])
	used=int(results['memUsed'][0])
	perFree=(1.00*memFree/memTotal*100)
	load = float(results['load'][2])	
	stat="| load=%s;0; memfree=%s;0; buffers=%s;0; cached=%s;0; free=%s;0; total=%s;0; used=%s;0;" % (load,perFree,buffers,cached,rawFree,memTotal,used)
	#chck physical memory levels
	
	if perFree < cFree:
		critical('Free memory is < %s%% current %s %s' % (cFree,perFree,stat))
	elif perFree < wFree:
		warn('Free memory is < %s%% current %s %s' %(wFree,perFree,stat))

	#check load Averages, checks on NAgios run every 5 mins, so we want the 5 min load average [2]
	if load > cLoad:
		critical('5 minute average load is > %s current %s %s' % (cLoad,load,stat))
	elif load > wLoad:
		warn('5 minute average load is > %s current %s %s' % (wLoad,load,stat))

	ok('All is well%s' % stat)
	

if __name__ == '__main__':
        main()



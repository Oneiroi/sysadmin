#!/usr/local/bin/python

#
# RedHat Cluster Check
# Created by David Busby
# Copyright (c) 2010 Psycle Interactive Ltd, David Busby
#
#
"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

import os,sys,getopt
TAG='RH_CLUSTER_CHECK'
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
        print 'replace me'
        sys.exit(1)

def main():
        #import required mods
        try:
                import netsnmp
        except ImportError, e:
                critical('Failed to load netsnmp, this module is required, you will need to install net-snmp >= 5.4.2.1 and compile the python bindings')

        opts, args = getopt.getopt(sys.argv[1:],"hs:c:",["help","output="])
	
	host = ''
	community = ''
        for o, a in opts:
                if o in ('-h', '--help'):
                        usage()
                elif o == '-s':
                	host = a
                elif o == '-c':
                        community = a

	if len(host) == 0 or len(community) == 0:
		usage()
		sys.exit(1)

	#WHAT A PAIN IN THIS ASS THIS WAS!

	rhc_oid = '.1.3.6.1.4.1.2312.8'
	data_oids = { 
				'rhcMIBVersion':'.1.1',
				'rhcClusterName':'.2.1',
				'rhcClusterStatusCode':'.2.2',
				'rhcClusterStatusDesc':'.2.3',
				'rhcClusterVotesNeededForQuorum':'.2.4',
				'rhcClusterVotes':'.2.5',
				'rhcClusterQuorate':'.2.6',
				'rhcClusterNodesNum':'.2.7',
				'rhcClusterNodesNames':'.2.8',
				'rhcClusterAvailNodesNum':'.2.9',
				'rhcClusterAvailNodesNames':'.2.10',
				'rhcClusterUnavailNodesNum':'.2.11',
				'rhcClusterUnavailNodesNames':'.2.12',
				'rhcClusterServicesNum':'.2.13',
				'rhcClusterServicesNames':'.2.14',
				'rhcClusterRunningServicesNum':'.2.15',
				'rhcClusterRunningServicesNames':'.2.16',
				'rhcClusterStoppedServicesNum':'.2.17',
				'rhcClusterStoppedServicesNames':'.2.18',
				'rhcClusterFailedServicesNum':'.2.19',
				'rhcClusterFailedServicesNames':'.2.20'}
	
	#Time to get the data
	results  = {}
	for item in data_oids:
		oid = '%s%s' % (rhc_oid,data_oids[item])
		oid = netsnmp.Varbind(oid)
		result = netsnmp.snmpwalk(      oid,
                                        Version = 2,
                                        DestHost = "%s" % host,
                                        Community = "%s" % community)
		results.update({item:result})

	
	#Check ClusterStatus code:
	#Taken from the RHC mib
	code2eng = {	1:' All services and nodes functional',
                	2:'Some services failed',
                	4:'Some services not running',
                	8:'Some nodes unavailable',
                	16:'Not quorate',
                	32:'Cluster stopped'}
	
	code = int(results['rhcClusterStatusCode'][0])
	if code > 1:
		if code == 2:
			nFailed = int(results['rhcClusterFailedServicesNum'][0])
			sFailed = results['rhcClusterFailedServicesNames']
			status = nFailed,'service(s) have failed, service names (%s)' % sFailed
		elif code == 4:
			nStopped = int(results['rhcClusterStoppedServicesNum'][0])
			sStopped = results['rhcClusterStoppedServicesNames']
			status = nStopped,'service(s) have been stopped, service names (%s)' % sStopped
		elif code == 8:
			nNode = int(results['rhcClusterUnavailNodesNum'][0])
			sNode = results['rhcClusterUnavailNodesNames']
			status = nNode,'node(s) are unavailable, node names (%s)' % sNode
		#todo, wtf is quorate?
		elif code == 16:
			status = 'no quorate'
		elif code == 32:
			status = 'Cluster has been stopped'
		
		critical(status)	
	else:
		ok(code2eng[code])
		

if __name__ == '__main__':
        main()


#!/usr/bin/env python

"""
    Author: David Busby (http://saiweb.co.uk)
    Program: check mysql replication
    Description: Compares two mysql connections checking slave and master status, assumes master-master relationship
    Copyright: Copyright (c) 2009,2010,2011,2012 David Busby (http://saiweb.co.uk)  & Psycle Interactive (http://psycle.com). All rights reserved.
    
    v0.1 - assumes master master relationship between two servers
"""

"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

from optparse import OptionParser,OptionGroup, OptParseError

import os,sys,optparse,re, time
import MySQLdb
from multiprocessing import Pool
from functools import partial

def _get_repl_data(opts,sID):
    '@todo: must be a cleaner way'
    s = 'ip = opts.%s' % sID
    exec s
    
    d = MySQLdb.connect(ip,opts.usr,opts.pwd)
    c = d.cursor()
    c.execute('SHOW MASTER STATUS;')
    m = c.fetchall()
    c.close()
    c = d.cursor()
    c.execute('SHOW SLAVE STATUS;')
    s = c.fetchall()
    try:
        return {sID:{'master':m,'slave':s}}
    except:
        return {}
 
def _setopt():
    useage = '';
    parser = OptionParser(usage="%prog [-v] -a 123.123.123.123 -b 123.123.123.123 -u username -p password -s 123", version="%prog 1.0")
    parser.add_option('-a','--server1', dest='srv1', help='fqdn or ip of server1 (master server with type: masterslave)') 
    parser.add_option('-b','--server2', dest='srv2', help='fqdn or ip of server2 (slave server with type: masterslave)')
    parser.add_option('-u','--user', dest='usr', help='Username to connect with')
    parser.add_option('-p','--password', dest='pwd', help='password to connect with')
    parser.add_option('-s','--behind', dest='behind', help='Max allow seconds behind master to warn [default: %default]', default=0)
    parser.add_option('-c','--behind_crit', dest='behind_crit', help='Max allowed seconds behind master to critical [default: %default]', default=1)
    parser.add_option('-l','--log_pos_crit', dest='log_pos_crit', help='Max allowed variance between binlog positions beyond which will trigger critical [default: %default]', default=10)
    parser.add_option('-w','--log_pos_warn', dest='log_pos_warn', help='Max allowed variance between binlog positions beyond which will trigger warning [default: %default]', default=5)
    
    parser.add_option('-v','--verbose', action='store_true', dest='verbose', default=False, help='make lots of noise [default: %default]')
    parser.add_option('-t','--type', dest='type', default='mastermaster', help='The replication type to check [default: %default]')
    
    return parser

TAG = 'CHECK_MYSQL_REPLICATION'
def ok(stat):
    print TAG,"OK -",stat
    sys.exit(0)
    
def warn(stat):
    print TAG,"WARN -",stat
    sys.exit(1)
    
def critical(stat):
    print TAG,"CRITICAL -",stat
    sys.exit(2);


def verbose(v,str):
    if v:
        print'%s: %s' % (time.time(),str)
     
 
if __name__ == '__main__': 
    optParse = _setopt()
    (options,args) = optParse.parse_args()
    
    verbose(options.verbose,'Check started, validating options passed')
    
    """ Options validation """
    if options.srv1 == None:
        optParse.error('Server1 is a required arg')
    if options.srv2 == None:
        optParse.error('Server2 is a required arg')
    if options.usr == None:
        optParse.error('Username is a required arg')
    if options.pwd == None:
        optParse.error('Password is a required arg')
        
    """Type dependant execution"""
    verbose(options.verbose,'Opt validation passed moving onto type')
    #@todo: as functionality is added, it can be broken out to individual functions to reduce code lines
    if options.type == 'mastermaster':
        verbose(options.verbose,'type is mastermaster')
        #Checking replication A -> B
        #We need A master and B slave status data.
        p = Pool(2)
        opts = {}
        #Map options as the first arg to the data collection function
        partial_repl = partial(_get_repl_data, options)
        #Now give .map 2 arguments to itterate
        d = p.map(partial_repl,['srv1','srv2'])

        #@todo: replace the positional lookups with associative lookups if at all possible, will negate issues in field order changes if it should ever occur.
        
        verbose(options.verbose,'slave running check')
        #Check slave is running on both servers!
        if d[0]['srv1']['slave'][0][10] != 'Yes':
            critical('Slave_IO is not running on srv1(%s) returned: %s'%(options.srv1,d[0]['srv1']['slave'][0][10]))
        if d[1]['srv2']['slave'][0][10] != 'Yes':
            critical('Slave_IO is not running on srv2(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave'][0][10]))
        if d[0]['srv1']['slave'][0][10] != 'Yes':
            critical('Slave_SQL is not running on srv1(%s) returned: %s'%(options.srv1,d[0]['srv1']['slave'][0][11]))
        if d[1]['srv2']['slave'][0][10] != 'Yes':
            critical('Slave_SQL is not running on srv2(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave'][0][11]))

        verbose(options.verbose,'slave running check passed')
        verbose(options.verbose,'srv1 -> srv2 binglog positional check')
        #Ok compare now A master to B slave using positional data.
        amLog = d[0]['srv1']['master'][0][0]
        amPos = d[0]['srv1']['master'][0][1]
        asLog = d[0]['srv1']['slave'][0][5]
        asPos = d[0]['srv1']['slave'][0][6]

        bmLog = d[1]['srv2']['master'][0][0]
        bmPos = d[1]['srv2']['master'][0][1]
        bsLog = d[1]['srv2']['slave'][0][5]
        bsPos = d[1]['srv2']['slave'][0][6]
        
        if amLog != bsLog:
            critical('[master-master] binary log mismatch! peer slave reports master binary log of %s local master reports %s' % (amLog,bsLog))

        if amPos != bsPos:
            critical('[master-master] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos)) 

        verbose(options.verbose,'srv1 -> srv2 binglog positional check passed')
        #Checking replication B->A
        verbose(options.verbose,'srv2 -> srv1 binglog positional check')

        if bmLog != asLog:
            critical('[master-master] binary log mismatch! local slave reports master binary log of %s peer master reports %s' % (bmLog,asLog))

        if bmPos != asPos:
            critical('[master-master] local slave and peer master out of sync! local slave log pos %d peer master log pos %d'%(bmPos,asPos))
        
        verbose(options.verbose,'srv2 -> srv1 binglog positional check passed')
        ok('master-master check completed, no issues were detected')

    elif options.type == 'masterslave':
        #We're assuming server2 is the slave and server1 is the master, because yknow the master "comes" first /endpun
        #As with master master we need to run the same checks but in this case only A->B and not B<-A
        verbose(options.verbose,'type is masterslave')
        #Checking replication A -> B
        #We need A master and B slave status data, note this could be changed to just give slabe data from server B time allowing (more efficient).
        p = Pool(2)
        opts = {}
        #Map options as the first arg to the data collection function
        partial_repl = partial(_get_repl_data, options)
        #Now give map 2 arguments to itterate
        d = p.map(partial_repl,['srv1','srv2'])
        
        #Check Slave threads @ B ONLY!
        if d[1]['srv2']['slave'][0][10] != 'Yes':
            critical('[master-slave] Slave_IO is not running on peer(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave'][0][10]))
        if d[1]['srv2']['slave'][0][10] != 'Yes':
            critical('[master-slave] Slave_SQL is not running on peer(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave'][0][11]))
        #Check replication
        amLog = d[0]['srv1']['master'][0][0]
        amPos = d[0]['srv1']['master'][0][1]
        bsLog = d[1]['srv2']['slave'][0][5]
        bsPos = d[1]['srv2']['slave'][0][6]
        
        if amLog != bsLog:
            critical('[master-slave] binary log mismatch! peer slave reports master binary log of %s local master reports %s' % (amLog,bsLog))
        if amPos != bsPos:
            critical('[master-slave] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos)) 
        #If we get here everything is good!
        ok('[master-slave] check completed, no issues were detected')
    else:
        critical('Type %s not supported' % (options.type))
        
    
    
    sys.exit(0)
    

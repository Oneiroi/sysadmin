#!/usr/bin/env python

"""
    Author: David Busby (http://saiweb.co.uk)
    Program: check mysql replication
    Description: Compares two mysql connections checking slave and master status, assumes master-master relationship
    Copyright: Copyright (c) 2008,2009,2010,2011,2012 David Busby (http://saiweb.co.uk)  & Psycle Interactive (http://psycle.com). All rights reserved.
    
    v0.1 - assumes master master relationship between two servers
"""

"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

from optparse import OptionParser,OptionGroup, OptParseError

import os,sys,optparse,re, time
import MySQLdb #Have to use MySQLdb as sqlalchemy fails to pickle for multiprocessing.
from multiprocessing import Pool
from functools import partial

def _get_repl_data(opts,sID):
    '@todo: must be a cleaner way'
    s = 'ip = opts.%s' % sID
    exec s
    
    d = MySQLdb.connect(ip,opts.usr,opts.pwd)
    c = d.cursor()
    c.execute('SHOW MASTER STATUS;')
    mdesc = c.description
    m = c.fetchall()
    c.close()
    c = d.cursor()
    c.execute('SHOW SLAVE STATUS;')
    sdesc = c.description
    s = c.fetchall()
    d.close()

    slave = {}
    master = {}
    #kludge together "assoc array" in dict form.
    i=0
    while i < mdesc.__len__():
        master.update({mdesc[i][0]:m[0][i]})
        i+=1
    i=0
    while i < sdesc.__len__():
        slave.update({sdesc[i][0]:s[0][i]})
        i+=1
    try:
        return {sID:{'master':master,'slave':slave}}
    except:
        return {}
 
def _setopt():
    useage = '';
    parser = OptionParser(usage="%prog [-v] -a 123.123.123.123 -b 123.123.123.123 -u username -p password", version="%prog 1.0")
    parser.add_option('-a','--server1', dest='srv1', help='fqdn or ip of server1 (master server with type: masterslave)') 
    parser.add_option('-b','--server2', dest='srv2', help='fqdn or ip of server2 (slave server with type: masterslave)')
    parser.add_option('-u','--user', dest='usr', help='Username to connect with')
    parser.add_option('-p','--password', dest='pwd', help='password to connect with')
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
        verbose(options.verbose,'slave running check')
        #Check slave is running on both servers!
        if d[0]['srv1']['slave']['Slave_IO_Running'] != 'Yes':
            critical('Slave_IO is not running on srv1(%s) returned: %s'%(options.srv1,d[0]['srv1']['slave']['Slave_IO_Running']))
        if d[1]['srv2']['slave']['Slave_IO_Running'] != 'Yes':
            critical('Slave_IO is not running on srv2(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave'][0][10]))
        if d[0]['srv1']['slave']['Slave_SQL_Running'] != 'Yes':
            critical('Slave_SQL is not running on srv1(%s) returned: %s'%(options.srv1,d[0]['srv1']['slave']['Slave_SQL_Running']))
        if d[1]['srv2']['slave']['Slave_SQL_Running'] != 'Yes':
            critical('Slave_SQL is not running on srv2(%s) returned: %s'%(options.srv2,d[1]['srv2']['slave']['Slave_SQL_Running']))
        #We've had (albeit rare) occasions where the Slave_IO and Slave_SQL report YES, but replication has halted due to an error
        #So lets check for error conditions. (Note: During this time, sqconds_behind_master was constantly 0, and only when the error cleared
        # did this update).
        if d[0]['srv1']['slave']['Last_Errno'] > 0:
            critical('Slave is in error on srv1(%s) retured: %d %s' %(options.srv1, d[0]['srv1']['slave']['Last_Errno'],d[0]['srv1']['slave']['Last_Error'])) 
        if d[1]['srv2']['slave']['Last_Errno'] > 0:
            critical('Slave is in error on srv2(%s) retured: %d %s' %(options.srv2, d[1]['srv2']['slave']['Last_Errno'],d[1]['srv2']['slave']['Last_Error']))
        #Finally throw a warning if seconds_behind_master > 0
        if d[0]['srv1']['slave']['Seconds_Behind_Master'] > 0:
            warn('Slave(%s) is behind Master(%s) by %d seconds' % (options.srv1,options.srv2,d[0]['srv1']['slave']['Seconds_Behind_Master']))
        if d[1]['srv2']['slave']['Seconds_Behind_Master'] > 0:
            warn('Slave(%s) is behind Master(%s) by %d seconds' % (options.srv2,options.srv1,d[1]['srv2']['slave']['Seconds_Behind_Master']))


        verbose(options.verbose,'slave running check passed')
        verbose(options.verbose,'srv1 -> srv2 binglog positional check')
        #Ok compare now A master to B slave using positional data.
        amLog = d[0]['srv1']['master']['File']
        amPos = d[0]['srv1']['master']['Position']
        asLog = d[0]['srv1']['slave']['Master_Log_File']
        asPos = d[0]['srv1']['slave']['Read_Master_Log_Pos']

        bmLog = d[1]['srv2']['master']['File']
        bmPos = d[1]['srv2']['master']['Position']
        bsLog = d[1]['srv2']['slave']['Master_Log_File']
        bsPos = d[1]['srv2']['slave']['Read_Master_Log_Pos']
        
        if amLog != bsLog:
            critical('[master-master] binary log mismatch! peer slave reports master binary log of %s local master reports %s' % (bsLog,amLog))

        if amPos != bsPos:
            if (amPos - bsPos) >= options.log_pos_crit:
                critical('[master-master] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos))
            elif (amPos - bsPos) >= options.log_pos_warn:
                warn('[master-master] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos))

        verbose(options.verbose,'srv1 -> srv2 binglog positional check passed')
        #Checking replication B->A
        verbose(options.verbose,'srv2 -> srv1 binglog positional check')

        if bmLog != asLog:
            critical('[master-master] binary log mismatch! local slave reports master binary log of %s peer master reports %s' % (asLog,bmLog))

        if bmPos != asPos:
            if (bmPos - asPos) >= options.log_pos_crit:
                critical('[master-master] local slave and peer master out of sync! local slave log pos %d peer master log pos %d'%(asPos,bmPos))
            elif (bmPos - asPos) >= options.log_pos_warn:
                warn('[master-master] local slave and peer master out of sync! local slave log pos %d peer master log pos %d'%(asPos,bmPos))
        
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
        if d[1]['srv2']['slave']['Slave_IO'] != 'Yes':
            critical('[master-slave] Slave_IO is not running on peer(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave']['Slave_IO']))
        if d[1]['srv2']['slave']['Slave_SQL'] != 'Yes':
            critical('[master-slave] Slave_SQL is not running on peer(%s) returned: %s'%(options.srv2,d[0]['srv2']['slave']['Slave_SQL'])
        #Check replication
        amLog = d[0]['srv1']['master']['Position']
        amPos = d[0]['srv1']['master']['File']
        bsLog = d[1]['srv2']['slave']['Master_Log_File']
        bsPos = d[1]['srv2']['slave']['Read_Master_Loig_Pos']
        
        if amLog != bsLog:
            critical('[master-slave] binary log mismatch! peer slave reports master binary log of %s local master reports %s' % (bsLog,amLog))
        if amPos != bsPos:
            if (amPos - bsPos) >= options.log_pos_crit:
                critical('[master-master] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos))
            elif (amPos - bsPos) >= options.log_pos_warn:
                warn('[master-master] peer slave and local master out of sync! peer slave log pos %d local master log pos %d'%(amPos,bsPos)) 
        #If we get here everything is good!
        ok('[master-slave] check completed, no issues were detected')
    else:
        critical('Type %s not supported' % (options.type))
        
    
    
    sys.exit(0)
    

#!/usr/bin/env python

"""
    Author: David Busby (http://saiweb.co.uk)
    Program: check mysql replication
    Description: Compares two mysql connections checking slave and master status, assumes master-master relationship
    Copyright: Copyright (c) 2009 David Busby (http://saiweb.co.uk)  & Psycle Interactive (http://psycle.com). All rights reserved.
    
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


class check_mastermaster:
    
    def __init__(self,options):
        self.srvA = options.srv1
        self.srvB = options.srv2
        self.usr = options.usr
        self.pwd = options.pwd     
    
    def _exec(self, cmd):
        prg = os.popen(cmd,"r")
        str = ''
        for line in prg.readlines():
            str += line
        return str.rstrip('\n')
    
    def _get_slave_status(self):
        d   = MySQLdb.connect(self.srvA,sef.usr,self.pwd,db="information_schema")
        c   = d.cursor()
        r   = c.execute("SHOW SLAVE STATUS\G")
        return c.fetchall()
        
        return {'srvA':self._exec('mysql -h %s -u %s -p%s -e "show slave status\G"' % (self.srvA,self.usr,self.pwd)),'srvB':self._exec('mysql -h %s -u %s -p%s -e "show slave status\G"' % (self.srvB,self.usr,self.pwd))}
    
    def _get_master_status(self):
        return {'srvA':self._exec('mysql -h %s -u %s -p%s -e "show master status\G"' % (self.srvA,self.usr,self.pwd)),'srvB':self._exec('mysql -h %s -u %s -p%s -e "show master status\G"' % (self.srvB,self.usr,self.pwd))}
          
    def slave_status(self):
        raw = self._get_slave_status()
        data = {}
        
        srvALines = raw['srvA'].split('\n')
        srvBLines = raw['srvB'].split('\n')
        
        data.update({'srvA':self.lines_2_dict(srvALines),'srvB':self.lines_2_dict(srvBLines)})
        
        return data
    
    def master_status(self):
       raw = self._get_master_status()
       data = {}
       
       srvALines = raw['srvA'].split('\n')
       srvBLines = raw['srvB'].split('\n')
        
       data.update({'srvA':self.lines_2_dict(srvALines),'srvB':self.lines_2_dict(srvBLines)})
       
       return data      
   
    def lines_2_dict(self,lines):
       i=0
       data={}
       for line in lines:
           """Skip first line from \G output"""
           if i == 0:
               i +=1
               continue
           else:
               """data.update({line.split(':')[0].strip():line.split(':')[1].strip()})"""
               try:
                   data.update({line.split(':')[0].strip():line.split(':')[1].strip()})
               except IndexError:
                   continue
    
       return data
       
def usage():
    sys.exit(1)
    
def _setopt():
    useage = '';
    parser = OptionParser(usage="%prog [-vi] -a 123.123.123.123 -b 123.123.123.123 -u username -p password -s 123", version="%prog 1.0")
    parser.add_option('-a','--server1', dest='srv1', help='fqdn or ip of server1') 
    parser.add_option('-b','--server2', dest='srv2', help='fqdn or ip of server2')
    parser.add_option('-u','--user', dest='usr', help='Username to connect with')
    parser.add_option('-p','--password', dest='pwd', help='password to connect with')
    parser.add_option('-s','--behind', dest='behind', help='Max allow seconds behind master to warn [default: %default]', default=0)
    parser.add_option('-c','--behind_crit', dest='behind_crit', help='Max allow seconds behind master to critical [default: %default]', default=1)
    parser.add_option('-l','--log_pos_crit', dest='log_pos_crit', help='Max allowed variance between binlog positions beyond which will trigger critical [default: %default]', default=10)
    parser.add_option('-w','--log_pos_warn', dest='log_pos_warn', help='Max allowed variance between binlog positions beyond which will trigger warning [default: %default]', default=5)
    
    parser.add_option('-v','--verbose', action='store_true', dest='verbose', default=False, help='make lots of noise [default: %default]')
    parser.add_option('-t','--type', dest='type', default='mastermaster', help='The replication type to check [default: %default]')
    
    group = OptionGroup(parser, "ALPHA Options",
                    "Caution: use these options at your own risk.  ")
    group.add_option('-i','--integrity', action='store_true', dest='integrity', default=False, help='Perform an integrity check by comparing data length of two random tables (ALPHA) [default: %default]')
    parser.add_option_group(group)


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


def _toint(str):
    
    try:
        return int(''.join([c for c in str if c in '1234567890']))
    except ValueError, e:
        critical('_toint() error %s' % (e))

def verbose(v,str):
    if v:
        print'%s: %s' % (time.time(),str)
        
def main():
    
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
    if options.type == 'mastermaster':
        verbose(options.verbose,'mastermaster type selected, aquiring slave dataset')
        check = check_mastermaster(options)
        data = check.slave_status()
        verbose(options.verbose,'slave dataset aquisition complete, aquiring master dataset')
        mdata = check.master_status()
        verbose(options.verbose,'Validating Datasets')
        
        """todo: may want to add validation for all used keys here, presently this is just a crude validation to ensure we actually have data"""
        try:
            i=0
            if data['srvA']['Slave_IO_Running'] != 'Yes':
                i+=1
            if data['srvB']['Slave_IO_Running'] != 'Yes':
                i+=1
        except KeyError:
            verbose(options.verbose,'Slave Dataset validation failed')
            critical('Slave dataset(s) missing required data, check server connection and credentials')
        
        try:
            i=0
            if mdata['srvA']['File'] != 'Yes':
                i+=1
            if mdata['srvB']['File'] != 'Yes':
                i+=1
        except KeyError:
            verbose(options.verbose,'Master Dataset validation failed')
            critical('Master dataset(s) missing required data, check server connection and credentials')    
            
        
        verbose(options.verbose,'Validating slave IO is in running state')
        """check slave IO state"""
        if data['srvA']['Slave_IO_Running'] != 'Yes':
            critical('Server A (%s) slave not running, returned status ("%s") lasterror ("%s")' % (options.srv1,data['srvA']['Slave_IO_Running'],data['srvA']['Last_Error']))
        elif data['srvB']['Slave_IO_Running'] != 'Yes':
            critical('Server B (%s) slave not running, returned status ("%s") lasterror ("%s")' % (options.srv1,data['srvB']['Slave_IO_Running'],data['srvB']['Last_Error']))
        """ check slave SQL state"""
        if data['srvA']['Slave_SQL_Running'] != 'Yes':
            critical('Server A (%s) slave SQL running, returned status ("%s") lasterror ("%s")' % (options.srv1,data['srvA']['Slave_SQL_Running'],data['srvA']['Last_Error']))
        elif data['srvB']['Slave_SQL_Running'] != 'Yes':
            critical('Server B (%s) slave SQL running, returned status ("%s") lasterror ("%s")' % (options.srv1,data['srvB']['Slave_SQL_Running'],data['srvB']['Last_Error']))
        
        verbose(options.verbose,'Validating slave time behind master critical level')
        
        if data['srvA']['Seconds_Behind_Master'] == 'NULL':
            critical('Server A Seconds_Behind_Master returned NULL')
        elif data['srvB']['Seconds_Behind_Master'] == 'NULL':
            critical('Server B Seconds_Behind_Master returned NULL') 
        
        if _toint(data['srvA']['Seconds_Behind_Master']) > options.behind_crit:
            critical('Server A (%s) seconds behind master (%s) exceeds critical level (%s)' % (options.srv1,data['srvA']['Seconds_Behind_Master'],options.behind_crit))
        elif _toint(data['srvB']['Seconds_Behind_Master']) > options.behind_crit:
            critical('Server B (%s) seconds behind master (%s) exceeds critical level (%s)' % (options.srv1,data['srvB']['Seconds_Behind_Master'],options.behind_crit))
        
        verbose(options.verbose,'Validating slave time behind master warning level')
            
        if _toint(data['srvA']['Seconds_Behind_Master']) > options.behind:
            warn('Server A (%s) seconds behind master (%s) exceeds warning level (%s)' % (options.srv1,data['srvA']['Seconds_Behind_Master'],options.behind))
        elif _toint(data['srvB']['Seconds_Behind_Master']) > options.behind:
            warn('Server B (%s) seconds behind master (%s) exceeds warning level (%s)' % (options.srv1,data['srvB']['Seconds_Behind_Master'],options.behind))
            
        verbose(options.verbose,'Slave validation complete, proceeding with master-slave comparitive checks')
        
        verbose(options.verbose,'Proceeding with binary log filename comparrison')
        
        if data['srvA']['Master_Log_File'] != mdata['srvB']['File']:
            critical('Binlog verification failed, Server A slave reports master file (%s) Server B Master reports file (%s)' % (data['srvA']['Master_Log_File'],mdata['srvB']['File']))
        elif data['srvB']['Master_Log_File'] != mdata['srvA']['File']:
            critical('Binlog verification failed, Server B slave reports master file (%s) Server A Master reports file (%s)' % (data['srvB']['Master_Log_File'],mdata['srvA']['File']))
        
        verbose(options.verbose,'Proceeding with binary log position comparrison')
        
        """
        todo:
        
        BUG: due to the sequential data sampling, there is on ave a 0.2s delay, this coupled with the high transactions per ec occuring on the servers means that on ave
        the offset in the binlog increases by 416 in 0.02s (20ms), 20800 offset / sec the only way to solve this is a concurrent 'grab' of the datasets
        
        a stored procedure on each server to return a single dataset will reduce the delay in data capture but not eliminate it, it may not be feasible to use binary log position as a means of checking replication between servers
        simply due to the delay however small it may be in data aquisition, in a high load environment
        
        But even with the sproc in place the delay is not removed entirely due to the sequential query, forking the data sample into concurrent processes would further reduce this delay but not remove it!
        If ANY delay occurs in netowrk/querytime/insert one of a million reasons here, the offset will not be idential and always return an error.
        
        _THEORY_: _IF_ it is possible to return both datasets (master & slave) in a single query, via a forked() concurrent capture and _IF_ it is possble to 'tag' the dataset with a hash of the current epoch time down to the nano second
        if _MAY_ be possible to run this check, _IF_ the hashes match indicating the EXACT same point in time on both servers.
        
        HOWEVER as the current ping time server to server is 0.14ms on average (0.00014s) this will not be possible, as 0.14ms = 140,000ns
        
        As such the following checks are commnted out
        
        """
        #if data['srvA']['Read_Master_Log_Pos'] != mdata['srvB']['Position']:
        #    verbose(options.verbose, 'binlog pos differs on Server A slave and Server B master')
        #    if _toint(data['srvA']['Read_Master_Log_Pos']) > _toint(mdata['srvB']['Position']):
        #       verbose(options.verbose, 'Server A Slave ahead of Server B Master, this should never happen triggering critical')
        #       critical('Binlog position verification failed, Server A slave reports read pos (%s) Server B Master reports file pos (%s)' % (data['srvA']['Read_Master_Log_Pos'],mdata['srvB']['Position']))
        #    elif _toint(data['srvA']['Read_Master_Log_Pos']) < _toint(mdata['srvB']['Position']): 
        #        verbose(options.verbose, 'Server A Slave behind Server B Master')
        #        diff = _toint(mdata['srvB']['Position']) - _toint(data['srvA']['Read_Master_Log_Pos'])
        #        if diff > options.log_pos_crit:
        #            verbose(options.verbose, 'Critical threshold exceeded')
        #            critical('Binlog position verification failed, Server A slave reports read pos (%s) Server B Master reports file pos (%s) diff(%s)' % (data['srvA']['Read_Master_Log_Pos'],mdata['srvB']['Position'],diff))
        #        elif diff > options.log_pos_warn:
        #            verbose(options.verbose, 'Warning threshold exceeded')
        #            warn('Binlog position verification failed, Server A slave reports read pos (%s) Server B Master reports file pos (%s) diff(%s)' % (data['srvA']['Read_Master_Log_Pos'],mdata['srvB']['Position'],diff))
        #        else:
        #            verbose(options.verbose, 'Positional difference is within acceptable bounds')
                
        #elif data['srvB']['Read_Master_Log_Pos'] != mdata['srvA']['Position']:
        #    verbose(options.verbose, 'binlog pos differs on Server B slave and Server A master')
        #    if _toint(data['srvB']['Read_Master_Log_Pos']) > _toint(mdata['srvA']['Position']):
        #       verbose(options.verbose, 'Server B Slave ahead of Server A Master, this should never happen triggering critical')
        #       critical('Binlog position verification failed, Server B slave reports read pos (%s) Server A Master reports file pos (%s)' % (data['srvB']['Read_Master_Log_Pos'],mdata['srvA']['Position']))
        #    elif _toint(data['srvB']['Read_Master_Log_Pos']) < _toint(mdata['srvA']['Position']): 
        #        verbose(options.verbose, 'Server B Slave behind Server A Master')
        #        diff = _toint(mdata['srvA']['Position']) - _toint(data['srvB']['Read_Master_Log_Pos'])
        #        if diff > options.log_pos_crit:
        #            verbose(options.verbose, 'Critical threshold exceeded')
        #            critical('Binlog position verification failed, Server B slave reports read pos (%s) Server A Master reports file pos (%s) dff(%s)' % (data['srvB']['Read_Master_Log_Pos'],mdata['srvA']['Position'],diff))
        #        elif diff > options.log_pos_warn:
        #            verbose(options.verbose, 'Warning threshold exceeded')
        #            warn('Binlog position verification failed, Server B slave reports read pos (%s) Server A Master reports file pos (%s) diff(%s)' % (data['srvB']['Read_Master_Log_Pos'],mdata['srvA']['Position'],diff))
        #       else:
        #            verbose(options.verbose, 'Positional difference is within acceptable bounds')
        
        verbose(options.verbose,'Positional comparrison completed, mastermaster replication is running within acceptable bounds, triggering OK')
        
        stat  = '| server_a_slave_pos=%s;0; server_b_slave_pos=%s;0; server_a_master_pos=%s;0; server_b_master_pos=%s;0;' % (data['srvA']['Read_Master_Log_Pos'],data['srvB']['Read_Master_Log_Pos'],mdata['srvA']['Position'],mdata['srvB']['Position'])
        ok('Master-Master reports OK server A (%s) Server B (%s)%s' % (options.srv1, options.srv2,stat))
                        
        
    elif option.type == 'somethingelse':
        print 'do somethingelse'
    else:
        critical('Type %s not supported' % (options.type))
        
    
    
    sys.exit(0)
    
    
if __name__ == '__main__':
    main()

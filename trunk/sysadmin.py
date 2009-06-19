#!/usr/bin/env python
"""
    @Author: David Busby (http://saiweb.co.uk)
    @Program: sysadmin
    @Description: Helper script for day to day sysadmin
    @Copyright: Copyright (c) 2009 David Busby.
    @License: http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA
"""
try:
    import ConfigParser,os,sys,re,time
    from zlib import crc32
    from optparse import OptionParser,OptionGroup, OptParseError
except ImportError, e:
    print 'Missing Library'
    print e
    sys.exit(1)

info = sys.version_info
version = (info[0] + ((info[1]*1.00)/10))

if version >= 2.5:
    try:
        import hashlib
    except ImportError, e:
        print 'Missing Library'
        print e
        sys.exit(1)
else:
    print 'Your python version is < 2.5 (%s.%s)' % (version,info[2])
    print 'hashlib has not been loaded, checksum functionality will not be enabled'



class sysadmin:
    
    def __init__(self):
        
        self.var = ''
        cwd = os.getcwd()
        cfgPath = "%s%s" % (sys.path[0],'/conf/sysadmin.conf')

        cfg = ConfigParser.RawConfigParser()
        cfg.read(cfgPath)

        try:
            self.v = cfg.getboolean('sysadmin', 'verbose')
            self.homedir = cfg.get('core', 'homedir')
            self.shell = cfg.get('core', 'shell')
            self.adduser = cfg.get('core','adduser')
            self.vhosts = cfg.get('core','vhosts')
            self.mkdir = cfg.get('core','mkdir')
            self.chown = cfg.get('core','chown')
            
        except ConfigParser.NoOptionError and ConfigParser.NoSectionError, e:
            #cant use error func here as uses verbose funtion
            print 'Config file error: ',cfgPath
            print e
            sys.exit(0);
            
    def webuser(self,opts):
        self.verbose('webuser()')
        homedir = self.homedir % (opts['usr'])
        cmd = self.adduser % (homedir, self.shell, opts['usr'])
        self._exec(cmd)
        cmd = self.mkdir % ('%s/%s' % (homedir,'public_html'))
        self._exec(cmd)
    
    def _get_filesize(self,path):
        try:
            return os.path.getsize(path)
        except OSError, e:
            self.error(e)
    
    def checksum(self,path):
        self.verbose('checksum()')
        
        if version >= 2.5:
            data = self._readfile(path)
            chk = self._checksum(data)
            print '--- Checksums for',path,' ---'
            print 'MD5: ',chk['md5']
            print 'CRC32: ',chk['crc32']
        else:
            self.error('Attempted to run checksum with incorrect python version, must be >= 2.5  (current %s)' % (version))
    
    def _readfile(self,path):
        self.verbose('_readfile(%s)' % (path))
        #bytes before prompting occurs
        limit = 30 * 1024 * 1024
        
        if self._get_filesize(path) > limit:
            self.verbose('Large file detected')
            size = round((self._get_filesize(path)/1024/1024),2) 
            
            print 'Large file detected, please ensure you have enough available memory to process this file before proceeding'
            print 'It is not recomended that you process this file on a live server'
            
            response = raw_input('The file is %sMB, are you sure you wish to load this into memory? (y/n):' % (size))
            
            while response not in ('y','n'):
                print 'Invalid response, please enter y or n'
                response = raw_input('The file is %sMB, are you sure you wish to load this into memory? (y/n):' % (size))
                
            if response == 'n':
                self.verbose('User decided not to proceed')
                print 'Exiting on user request...'
                sys.exit(0)
            elif response == 'y':
                self.verbose('User decided to proceed')
                print 'Proceeding on user request ... be advised large files take a long time to process'
                    
        try:
            f = file(path, 'r')
            data = f.read()
            f.close()
        except IOError, e:
            self.error(e)
        return data
    
    def _checksum(self,data):
        self.verbose('_checksum()')
        if version >= 2.5:
            m = hashlib.md5()
            m.update(data)
            return {'md5':m.hexdigest(),'crc32':crc32(data) & 0xffffffff}
        else:
            return 'Your version of python does not support hashlib, checksum has not been calculated'
    
    def _iconv(self,opts):
        self.verbose('_iconv()')
        tmp = opts
        opts = iconv_opts()
        try:
            opts.path = tmp[0]
            opts.cs_from = tmp[1]
            opts.cs_to = tmp[2]
        except IndexError, e:
            self.verbose('Required data is missing')

               
        if (hasattr(opts, 'path') and opts.path != None) and (hasattr(opts, 'cs_from') and opts.cs_from != None) and (hasattr(opts, 'cs_to') and opts.cs_to != None):
            sql = self._readfile(opts.path)
            
            if hasattr(opts, 'checksum') and opts.checksum == True:
                src_checksum = self._checksum(sql)
            try: 
                tgt = unicode(sql,opts.cs_from).encode(opts.cs_to)
            except UnicodeEncodeError, e:
                self.error(e)
            
            try:
                out_path = '%s.%s' % (opts.path,opts.cs_to)
                f = file(out_path,'w+')
                f.write(tgt)
                f.close()
            except IOError, e:
                self.error(e)
            
            if hasattr(opts, 'checksum') and opts.checksum == True:
                tgt_checksum = self._checksum(tgt)
                
                print 'src checksum: ', src_checksum
                print 'tgt checksum: ', tgt_checksum
                print 'output file: ', out_path
                                         
        else:
            print 'Path, source charset and dest charset are required'
            sys.exit(1)
        
    def appmem(self,filter):
        self.verbose('appmem(%s)' % (filter))
        cmd = 'ps aux | grep "%s" | grep -v "grep" | grep -v "%s"' % (filter,sys.argv[0])
        data = self._exec(cmd)
        data = data.split('\n')
        raw = []
        set = []
        for line in data:
            raw = line.split(' ')
            dat = []
            for tmp in raw:
                if len(tmp) > 0:
                    dat.append(tmp)
            set.append(dat)
        vsz = 0
        rss = 0
        
        for line in set:
            try:
                vsz += int(line[4])
                rss += int(line[5])
            except IndexError, e:
                self.error(e)
        count = len(set)
        print '--- Memory Usage Report For %s ---' % (filter)
        print 'PID Count: %s' % (count)
        print 'Shared Memory Usage: %sMB' % (round((vsz/count)/1024,2))
        print 'Total Resident Set Size: %sMB' % (round((rss/1024),2))
        print 'MEM/PID: %sMB' % (round((rss/count)/1024,2)) 
        
        
    def error(self,e):
        self.verbose('error()')
        print 'ERROR: ',e
        sys.exit(1)
        
    def verbose(self,str):
        if self.v:
            print'%s: %s' % (time.time(),str)
        
    def _exec(self, cmd):
        self.verbose('_exec(%s)' % (cmd))
        prg = os.popen(cmd,"r")
        str = ''
        for line in prg.readlines():
            str += line

        return str.rstrip('\n')

"""
stubb class for iconv charset opts
"""
class iconv_opts:
    path = None
    cs_from = None
    cs_to = None
    checksum = True
    
def usage():
  
    
    help = """
    
    ### Sysadmin Script by D.Busby                                          ###
    ### http://saiweb.co.uk                                                 ###
    ### license: http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA ###
    
    %s -c command -d csv,seperated,data
    
    Available commands:
    
        iconv - This command is used to converted between charecter encoding
        Example: -c iconv -d /path/to/file.ext,latin-1,utf-8
        
        appmem - This commaned is used to estimate the memory usage of a currently running process
        Example: -c appmem -d filter
        Note: filter can be the process name i.e. httpd or anything else you wish to filter by i.e. PID
        
        webuser - This command is used to create a new webuser (incomplete at present do not use)
        Example: -c webuser -d username
        Notes: The majority of the configuration for this command take place under the advanced section of the config file
        
        checksum - This command will read a file and provide crc32 and md5 checksums, this does however require Python 2.5 or higher to run
        Example: -c checksum -d /path/to/file
        Notes: A Python version of 2.5 or higher is required, also if a file larger than 30MB is selected the user will be required to confirm before proceeding
    """ % (sys.argv[0])
    
    return help

def main():
    sa = sysadmin()
    sa.verbose('main()')         
    parser = OptionParser(usage=usage(), version="%prog 1.0")
    parser.add_option('-c','--command', dest='command', help='Command to run')
    parser.add_option('-d','--data', dest='data', help='CSV Style data')
    
    (options,args) = parser.parse_args()
    
    sa.verbose('args parsed')
    
    if options.command == None:
        parser.error('Command is a required input')
    elif options.data == None:
        parser.error('Data is a required input')
    else:
        sa.verbose('Command: %s' % (options.command))
        opts = options.data.split(',')
        
        #todo: replace this, couldn't get switch statements working properly!
        if options.command == 'iconv':
            sa._iconv(opts)
        elif options.command == 'appmem':
            sa.appmem(opts[0])
        elif options.command == 'checksum':
            sa.checksum(opts[0])
    
       
    
                
if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
    @Author: David Busby (http://saiweb.co.uk)
    @Program: sysadmin
    @Description: Helper script for day to day sysadmin
    @Copyright: Copyright (c) 2009 David Busby.
    @License: http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA
"""
try:
    import ConfigParser,os,sys,re,time,string,socket,threading,thread
    from zlib import crc32
    from optparse import OptionParser,OptionGroup, OptParseError
except ImportError, e:
    print 'Missing Library'
    print e
    sys.exit(1)

#===============================================================================
# Check the current running version of python
# @todo: this should be improved
#===============================================================================
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


#===============================================================================
# The main sysadmin class
#===============================================================================
class sysadmin:
    
#===============================================================================
#    sysadmin construct, loads config and sets up class variables
#===============================================================================
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
            self.rbls = cfg.get('sysadmin','rbl_list')
            self.rbls = self.rbls.split(',')
            #self.ssl_crt = cfg.get('core','ssl_crt')
            #self.ssl_key = cfg.get('core','ssl_key')
            #self.ssl_vhost = cfg.get('core','ssl_vhost')
            
        except ConfigParser.NoOptionError and ConfigParser.NoSectionError, e:
            #cant use error func here as uses verbose funtion
            print 'Config file error: ',cfgPath
            print e
            sys.exit(0)
            
#===============================================================================
#    _get_filesize, attempts to get the filesize in bytes of the provided path
#    @param path: string
#===============================================================================
    def _get_filesize(self,path):
        try:
            return os.path.getsize(path)
        except OSError, e:
            self.error(e)
#===============================================================================
#    windowsreturn, this function is used to strip out windows file encodings, such as \r\n for carriage returns
#    @param path: string
#===============================================================================
    def windowsreturn(self,path):
        data = self._readfile(path)
        data = re.subn('\r','',data)
        if data[1] > 0:
            str = data[0]
            q = 'I am about to replace %s occurances of \\r and overwrite the file, are you sure you want to proceed?' % (data[1])
            response = raw_input(q)
            while response not in ('y','n'):
                print 'Invalid response, please enter y or n'
                response = raw_input(q)
            if response == 'y':
                self._writefile(path,str)
                print 'Done'
            elif response == 'n':
                print 'Aborted on user request'
        else:
            print 'I could not find any occurances of \\r in the provided file, no changes have been made'
#===============================================================================
#    checksum, this function returns the md5, and crc32 checksums, if the current running version is above 2.5
#    @param path: string
#===============================================================================
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
#===============================================================================
#    writefile, as the name suggest this function writes data to a file, it opens it up in w+ mode which truncates the file to zero length
#    then writes the data
#    @param path: string
#    @para data: string
#===============================================================================
    def _writefile(self,path,data):
        self.verbose('_writefile(%s)' % (path))
        try:
            f = file(path,'w+')
            f.write(data)
        except IOError, e:
            error = 'Failed to write data error(%s)' % (e)
            error = '%s Dumping data <<< START\n%s\n<<<END\n' % (e,data)
            self.error(e)
#===============================================================================
#    readfile, as the name sugges this function is used to read a file into memory, if the file is above 30mb, the user will be prompted to confirm
#    @param path: string 
#===============================================================================
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
            return {'md5':'hashlib not loaded','crc32':crc32(data) & 0xffffffff}
    
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
        
    def rblcheck(self,opts):
        try:
            ip = opts[0]
        except KeyError,e:
            self.error(e)
        
        tmp = string.split(ip,".")
        tmp.reverse()
        
        for rbl in self.rbls:
            lookup = string.join(tmp,".")+"."+rbl
            
            try:
                try:
                    addr = socket.gethostbyname(lookup)
                except socket.error, e:
                    addr=False
                    #print e
            except KeyboardInterrupt:
                print '\n^C Received Aborting RBL Check'
                sys.exit(0)
            
            if addr != False:
                print 'IP(%s) is listed at RBL(%s)' % (ip,rbl)
                print 'Returned: %s'  % (addr)
            else:
                print 'IP(%s) is not listed at RBL(%s)' % (ip,rbl)
    
    def httpd_stats(self,opts):
        #this was not fun to type!
        codes = {
                     100:{'desc':'continue','count':0},
                     101:{'desc':'switching protocol','count':0},
                     200:{'desc':'OK','count':0},
                     201:{'desc':'created','count':0},
                     202:{'desc':'accepted','count':0},
                     203:{'desc':'Non-Authoritative Information','count':0},
                     204:{'desc':'No content','count':0},
                     205:{'desc':'Reset content','count':0},
                     206:{'desc':'Partial content','count':0},
                     300:{'desc':'Multiple choices','count':0},
                     301:{'desc':'Moved permanently','count':0},
                     302:{'desc':'Found','count':0},
                     303:{'desc':'See other','count':0},
                     304:{'desc':'Not modified','count':0},
                     305:{'desc':'Use proxy','count':0},
                     #306 deprecated
                     307:{'desc':'Temporary redirect','count':0},
                     400:{'desc':'Bad request','count':0},
                     401:{'desc':'PUnauthorised','count':0},
                     402:{'desc':'Payment required','count':0},
                     403:{'desc':'Forbidden','count':0},
                     404:{'desc':'Not found','count':0},
                     405:{'desc':'Method not allowed','count':0},
                     406:{'desc':'Not acceptable','count':0},
                     407:{'desc':'Proxy Auth Required','count':0},
                     408:{'desc':'Request timeout','count':0},
                     409:{'desc':'Conflict','count':0},
                     410:{'desc':'Gone','count':0},
                     411:{'desc':'Length required','count':0},
                     412:{'desc':'Precondition Failed','count':0},
                     413:{'desc':'Request Entity Too Large','count':0},
                     414:{'desc':'Request-URI Too Long','count':0},
                     415:{'desc':'Unsupported Media Type','count':0},
                     416:{'desc':'Requested Range Not Satisfiable','count':0},
                     417:{'desc':'Expectation Failed','count':0},
                     500:{'desc':'Internal Server Error','count':0},
                     501:{'desc':'Not Implemented','count':0},
                     502:{'desc':'Bad Gateway','count':0},
                     503:{'desc':'Service Unavailable','count':0},
                     504:{'desc':'Gateway Timeout','count':0},
                     505:{'desc':'HTTP Version Not Supported','count':0}
                 }
        
        if os.path.isfile(opts[0]):
            raw = self._readfile(opts[0])
            lines = raw.split('\n')
            bytes = 0
            rcount = 0
            ips = {}
            
            for line in lines:
                dat = line.split(' ')
                #at this split the status code should be in dat[8] and the bytes transfered in dat[9]
                try:
                    ips[dat[0]]+=1
                except KeyError:
                    ips[dat[0]] = 1
                try:
                    rcode = re.split('\D+',dat[8])[0].replace(' ','')
                    if len(rcode) > 0:
                        rcode = self._toint(rcode)
                    else:
                        rcode = 0
                    tmp = re.split('\D+',dat[9])[0].replace(' ','')
                    if len(tmp) > 0:
                        bytes += self._toint(tmp)
                    else:
                        bytes += 0
                    try:
                        codes[rcode]['count'] += 1
                    except KeyError, e:
                        print 'Got invalid response code: ',rcode, 'DATA(',dat,')'
                    rcount += 1
                except IndexError, e:
                    print dat,e
            
            print '--- HTTP Code stats ---'    
            for code in codes:
                if codes[code]['count'] > 0:
                    print code,codes[code]['desc'],':',codes[code]['count']
            
            print '--- Bandwidth stats ---'
            print 'Requests:',rcount
            print 'Bytes:',bytes
            print 'Megabytes:',round((bytes/1024.00/1024.00),2)
            print 'Gigabytes:',round((bytes/1024.00/1024.00/1024.00),2)
            
            print '--- IP stats ---'
            print 'Unique IPs:',len(ips)
            
            items = ips.items()
            items.sort(key=lambda (k,v): (v,k), reverse=True)
            
            str ='Would you like to output the count for each ip?:'
            response = raw_input(str)
            while response not in ('y','n'):
                str = 'Invalid option, reply y or n:'
                response = raw_input(str)
            if response == 'y':
                for item in items:
                    print '%s: %s' % (item[0],item[1])
                        
        else:
            self.error('404 file not found! %s ' % (opts[0]))  
            
    def _toint(self,str):
        try:
            str = str.strip()
            return int(''.join([c for c in str if c in '1234567890']))
        except ValueError, e:
            self.error('_toint() error %s' % (e),exit=False)   
        
                          
    def error(self,e,exit=True):
        self.verbose('error()')
        print 'ERROR: ',e
        if exit:
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
    
    def _walkhash(self,path):
        from os.path import join, getsize
        data = []
        for root, dirs, files in os.walk(path):
            for fname in files:
                fpath = join(root,fname)
                fpath = string.replace(fpath,path,'')
                data.append({'path':fpath,'hash':self._checksum(fpath)})
        return data
    
    def filesystem_compare(self,opts):
        
        str ="""
Depending on the number of files and folders, this comparrison can take a very long time, and be quite heavy on CPU usage.
Are you sure you wish to continue?:"""
        response = raw_input(str)
        while response not in ('y','n'):
            str = 'Invalid option, reply y or n:'
            response = raw_input(str)
        if response == 'n':
            print 'Exiting on user request...'
            sys.exit(0)
        elif response == 'y':
            
            path = opts[0]
            path2 = opts[1]
            
            if not os.path.isdir(path):
                print 'Path is not directory:',path
                sys.exit(1)
            elif not os.path.isdir(path2):
                print 'Path is not directory:',path2
                sys.exit(1)
            else:
                #path1
                data1 = self._walkhash(path)
                #path2
                data2 = self._walkhash(path2)
                #paths
                paths1 = []
                paths2 = []
                hashes1 = {}
                hashes2 = {}
                for fdata in data1:
                    paths1.append(fdata['path'])
                    hashes1[fdata['path']] = fdata['hash']
                for fdata in data2:
                    paths2.append(fdata['path'])
                    hashes2[fdata['path']] = fdata['hash']
                print '--- Begin fscompare ---'
                print '-- Now comparing:',path,'to',path2
                
                for fpath in paths1:
                    if fpath not in paths2:
                        #- print 'Missing File:',fpath,'Does not exist in',path2
                        cmd = 'cp %s%s %s%s' % (path,fpath, path2,fpath)
                        print cmd
                    # elif (hashes1[fpath]['md5'] != hashes2[fpath]['md5']) or (hashes1[fpath]['crc32'] != hashes2[fpath]['crc32']):
                        # print 'File HASH fail:',fpath,'file hashes do not match'
                        #----------------------- print path,fpath,hashes1[fpath]
                        #---------------------- print path2,fpath,hashes2[fpath]
                        
                #--------------------- print '-- Now comparing:',path2,'to',path
#------------------------------------------------------------------------------ 
                #------------------------------------------ for fpath in paths2:
                    #----------------------------------- if fpath not in paths1:
                        #-- print 'Missing File:',fpath,'Does not exist in',path
                    # elif (hashes2[fpath]['md5'] != hashes1[fpath]['md5']) or (hashes2[fpath]['crc32'] != hashes1[fpath]['crc32']):
                        # print 'File HASH fail:',fpath,'file hashes do not match'
                        #---------------------- print path2,fpath,hashes2[fpath]
                        #----------------------- print path,fpath,hashes1[fpath]
                        
                print '--- End fscompare ---'
                        
            
                
        
#===============================================================================
#    This function is incomplete, do not use
#===============================================================================
    def netscan(self,cidr):
        str = """
This scanner is to be used at your own risk, and I advise only on a network where you have permission to scan.
This scanner is multithreaded so in large networks can cause high load on the system it is running from.
            
You must now confirm that you have the legal right to proceed with this scan.
        """
        print str
        
        str = 'Scanning networks can be illegal, are you sure you want to proceed? (y/n):'
        response = raw_input(str)
        while response not in ('y','n'):
            print 'Invalid optiion, reply y or n'
            response = raw_input(str)
        if response == 'n':
            print 'Exiting on user request...'
            sys.exit(0)
        elif response == 'y':
            str = """
You have chose to proceed with this network scan, you must now choose a scan type
p - Ping scan, attempts an ICMP ping of each ip in the suplied range
s - SYN ACK scan, stealth port scanning assumes all hosts are up (will not ping) and attempts SYN ACK of common ports
Scan type:"""
        response = raw_input(str)
        while response not in ('p','s'):
            print 'Invalid optiion, reply p or s'
            response = raw_input(str)
        net = IPv4Addr(cidr)
        print net
            
    
class pingthread(threading.Thread):
    def __init__(self, threadID,name,counter,ip,app):
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.ip =  ip
        self.app = app
        threading.Thread.__init__(self)
    
    def run(self):
        data = self.app._exec('ping -q -c2 %s' % (self.ip))
        search = re.compile('(\d) received')
        response = ('Host down','Partial Response','Host Alive')
        res = re.findall(search, data)
        if res:
            print response[int(res[0])]
        
#===============================================================================
# stubb class for iconv charset opts
#===============================================================================
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
    
        iconv - This command is used to convert a files contents character encoding
        Example: -c iconv -d /path/to/file.ext,latin-1,utf-8
        
        appmem - This command is used to estimate the memory usage of a currently running process
        Example: -c appmem -d filter
        Note: filter can be the process name i.e. httpd or anything else you wish to filter by i.e. PID
        
        checksum - This command will read a file and provide crc32 and md5 checksums, this does however require Python 2.5 or higher to run
        Example: -c checksum -d /path/to/file
        Notes: A Python version of 2.5 or higher is required, also if a file larger than 30MB is selected the user will be required to confirm before proceeding
        
        rblcheck - This command will attempt to check if the provided IP address is listed at several RBLs
        Example: -c rblcheck -d 123
        
        httpd_stats (BETA) - This command will attempt to provide rough statistics based on the provided apache log file.
        Example: -c httpd_status -d /path/to/access.log
        Notes: This function assumes combined output, this may not work with other log types
        
        windowsreturn (BETA) - This command will remove all \\r (^M) chars from a file, windows typically uses \\r\\n for carriage returns, this causes issues particularly when used in bash scripts
        Example: -c windowsreturn -d /path/to/file
        Notes: This will overwrite the original file, as such make sure you have a backup
        
        fscompare - This command will attempt to compare files between two directories, checking if they exist and their file hashes
        Example: -c fscompare -d /path/to/folder1,/path/toi/folder2
                
        
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
        elif options.command == 'webuser':
            sa.webuser(opts)
        elif options.command == 'rblcheck':
            sa.rblcheck(opts)
        elif options.command == 'httpd_stats':
            sa.httpd_stats(opts)
        elif options.command == 'windowsreturn':
            sa.windowsreturn(opts[0])
        elif options.command == 'fscompare':
            sa.filesystem_compare(opts)
        else:
            print 'Command not found "%s"' % (options.command)
       
    
                
if __name__ == "__main__":
    main()

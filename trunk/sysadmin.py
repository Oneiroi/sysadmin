#!/usr/bin/env python
"""
    @Author: David Busby (http://saiweb.co.uk)
    @Program: sysadmin
    @Description: Helper script for day to day sysadmin
    @Copyright: Copyright (c) 2009 David Busby.
    @License: http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA
"""
try:
    import ConfigParser,os,sys,re,time,string,socket,threading,thread,traceback
    from signal import signal, SIGTERM, SIGINT, SIGHUP
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
    import md5
    print 'Your python version is < 2.5 (%s.%s)' % (version,info[2])
    print 'hashlib has not been loaded, md5 has been loaded'


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
            sysexit()
    
    def progress(self,str):
        str = " %s" % str
        
        while len(str) < opts.slen:
            str = '%s ' % str    
        opts.slen = len(str)
        sys.stdout.write(str + '\r')
        sys.stdout.flush()
        
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
                sysexit()
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

#===============================================================================
# This function generates MD5 checksums    
#===============================================================================
    def _checksum(self,data):
        self.verbose('_checksum()')
        if version >= 2.5:
            m = hashlib.md5()
            if os.path.isfile(data):
                f = file(data,'r')
                s = self._get_filesize(data)
                offset = 0
                while offset < s:
                    m.update(f.read(1024))
                    offset += 1024
            else:
                m.update(data)
                    
            return {'md5':m.hexdigest()}
        else:
            m = md5.new()
            if os.path.isfile(data):
                f = file(data,'r')
                s = self._get_filesize(data)
                offset = 0
                while offset < s:
                    m.update(f.read(1024))
                    offset += 1024
            else:
                m.update(data)
            return {'md5':m.hexdigest()}
        
#===============================================================================
# This function provides iconv like functionality, and currently has a small amount of BOM detection
#===============================================================================
    def _iconv(self,opts):
        
        
        BOM={#src: http://code.activestate.com/recipes/363841/              
                    (0x00, 0x00, 0xFE, 0xFF) : "utf-32-be",        
                    (0xFF, 0xFE, 0x00, 0x00) : "utf-32-le",
                    (0xFE, 0xFF, None, None) : "utf-16-be", 
                    (0xFF, 0xFE, None, None) : "utf-16-le", 
                    (0xEF, 0xBB, 0xBF, None) : "utf-8",
                 }

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
            if opts.cs_from == opts.cs_to:
                print 'Source and Destination encodings are the same, aborting ...'
                sysexit(1)
            try:
                sF = file(opts.path, 'r')
                tPath = '%s.%s' % (opts.path, opts.cs_to)
                tF = file(tPath, 'w+')
                sSize = self._get_filesize(opts.path)
                offset = 0
                increment = 1024
                runBOM=False
                gotBOM=False
                lenBOM=0
                actual = 0
                while offset < sSize:
                    sData = sF.read(increment)
                    if runBOM == False:
                        runBOM = True
                        bytes = (byte1, byte2, byte3, byte4) = tuple(map(ord, sData[0:4]))
                        lenBOM=4
                        enc = BOM.get(bytes, None)
                        if not enc:
                            enc = BOM.get((byte1,byte2,byte3,None))
                            lenBOM=3
                            if not enc:
                                enc = BOM.get((byte1,byte2,None,None))
                                lenBOM=2
                        if enc:
                            gotBOM = True
                            if opts.cs_from != enc:
                                answer = raw_input('BOM FOUND: I detected %s please select the source encoding (%s/%s):' % (enc,opts.cs_from,enc))
                                while answer not in (enc,opts.cs_from):
                                    answer = raw_input('Invalid response (%s/%s):' % (opts.cs_from,enc))
                                if answer == opts.cs_to:
                                    print 'Source and Destination encodings are the same, aborting ...'
                                    sysexit(1)
                                opts.cs_from = answer
                    #string out the BOM
                    if gotBOM == True:
                        sData = sData[lenBOM:1024-lenBOM]
                                                                           
                    offset += increment
                    tData = unicode(sData,opts.cs_from).encode(opts.cs_to)
                    actual += len(tData)
                    tF.write(tData)
                    self.progress('Wrote: %s bytes' % (actual))
            except (IOError or UnicodeEncodeError), e:
                self.error(e)
                
            print 'Conversion complete: %s' % tPath
                                                    
        else:
            print 'Path, source charset and dest charset are required'
            sysexit(1)
 
#===============================================================================
# This function parses the output of ps aux to generate information on the memory allocations to a given process name       
#===============================================================================
    def appmem(self,filter):
        self.verbose('appmem(%s)' % (filter))
        cmd = 'ps aux | grep -i "%s" | grep -v "grep" | grep -v "%s"' % (filter,sys.argv[0])
        data = self._exec(cmd)
        data = data.split('\n')
        raw = []
        set = []
        #----------------------------------------------------- for line in data:
            #--------------------------------------------- raw = line.split(' ')
            #---------------------------------------------------------- dat = []
            #--------------------------------------------------- for tmp in raw:
                #---------------------------------------------- if len(tmp) > 0:
                    #------------------------------------------- dat.append(tmp)
            #--------------------------------------------------- set.append(dat)
        #--------------------------------------------------------------- vsz = 0
        #--------------------------------------------------------------- rss = 0
#------------------------------------------------------------------------------ 
        #------------------------------------------------------ for line in set:
            #-------------------------------------------------------------- try:
                #------------------------------------------- vsz += int(line[4])
                #------------------------------------------- rss += int(line[5])
            #--------------------------------------------- except IndexError, e:
                #------------------------------------------------- self.error(e)
        vsz = 0
        rss = 0
        cpuper = 0.0
        memper = 0.0
        
        count = 0
        regex = '[a-z\s]+[0-9]+\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9]+)\s+([0-9]+)'
        for line in data:
            tmp = re.split(regex, line)
            # 1 - % CPU
            # 2 - % MEM
            # 3 - VSZ
            # 4 - RSS
            vsz += int(tmp[3])
            rss += int(tmp[4])
            cpuper += float(tmp[1])
            memper += float(tmp[2])
            count += 1
            
        print '--- Memory Usage Report For %s ---' % (filter)
        print 'PID Count: %s' % (count)
        print 'Shared Memory Usage: %sMB' % (round((vsz/count)/1024,2))
        print 'Total Resident Set Size: %sMB' % (round((rss/1024),2))
        print 'MEM/PID: %sMB' % (round((rss/count)/1024,2))
        print '%%CPU: %s' % cpuper
        print '%%MEM: %s' % memper
#===============================================================================
# This function attempts to lookup against the configured RBL servers in an attempt to identify an RBL listing for the given ip address      
#===============================================================================
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
                sysexit(1)
            
            if addr != False:
                print 'IP(%s) is listed at RBL(%s)' % (ip,rbl)
                print 'Returned: %s'  % (addr)
            else:
                print 'IP(%s) is not listed at RBL(%s)' % (ip,rbl)

#===============================================================================
# This function gives rough stats from a 'combined' apache logfile
#===============================================================================
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
                     401:{'desc':'Unauthorised','count':0},
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
            self.progress(' Please wait getting file stats...')
            ltotal = 0;
            for line in open(opts[0],'r'):
                ltotal +=1
            print
            lcount = 0;
            bytes = 0
            rcount = 0
            
            ips = {}
            
            ltime = time.time()
            lline = 0
            linessec = 0
            eta = 0
            etastr = '--:--:--'              
            for line in open(opts[0],'r'):
                dat = re.split('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s-\s[^\]]+\]\s".*"\s([0-9]+)\s(-|[0-9]+)', line)
                
                #-------------------------------------------------------- 1 = ip
                #-------------------------------------------------------- 2 = HTTP code
                #-------------------------------------------------------- 3 = Bytes
                
                #increment count for this ip by one, or cerate a new entry if this is the first occurance
                try:
                    ips[dat[1]]+=1
                except:
                    ips[dat[1]] = 1
                
                try:
                    #check if we have an entry for the byte size transfered
                    if dat[3] == '-':
                        bytes += 0
                    else:
                        bytes += int(dat[3])
                            
                    #update response code stats
                    try:
                        codes[int(dat[2])]['count'] += 1
                    except KeyError, e:
                        print 'Got invalid response code: ',dat[2], 'DATA(',dat,')'
                    rcount += 1
                except IndexError, e:
                    print dat,e
                #import pdb; pdb.set_trace()
                lcount += 1
                ctime = time.time()
                if (ctime - ltime) >= 2:
                    #calc current processing speed
                    if ltime > 0:
                        linessec = round((lcount - lline) / (ctime - ltime),2)
                    ltime = ctime
                    lline = lcount
                    #give an ETA
                    if (linessec > 0):
                        eta = (ltotal - lcount) / linessec
                        m, s = divmod(eta, 60)
                        h, m = divmod(m, 60)
                        etastr = "%d:%02d:%02d" % (h, m, s)
                    else:
                        etastr = '--:--:--'

                    
                lper = round(((1.00*lcount)/(1.00*ltotal))*100.00,2)
                self.progress(' Parsed %s/%s lines (%s%%) %s/s ETA %s' % (lcount,ltotal,lper,linessec,etastr))
                
            print
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
            
            count = 0
            for item in items:
                count += 1
                print '%s: %s' % (item[0],item[1])
                if count == 10:
                    str ='Would you like to output the next 10?:'
                    response = raw_input(str)
                    while response not in ('y','n'):
                        str = 'Invalid option, reply y or n:'
                        response = raw_input(str)
                    if response == 'y':
                        count = 0
                    elif response == 'n':
                        sysexit()
                        
        else:
            self.error('404 file not found! %s ' % (opts[0]))  
#===============================================================================
#    basic hack str to int type        
#===============================================================================
    def _toint(self,str):
        if str.__class__ == 'str':
            try:
                str = str.strip()
                return int(''.join([c for c in str if c in '1234567890']))
            except ValueError, e:
                self.error('_toint() error %s' % (e),exit=False)   
        
#===============================================================================
#    wrapper to print out error and sys.exit(1)              
#===============================================================================
    def error(self,e,exit=True):
        self.verbose('error()')
        print 'ERROR: ',e
        if exit:
            sysexit(1)
#===============================================================================
#    verbose output function, prints out it verbose true
#===============================================================================
    def verbose(self,str):
        if self.v:
            print'%s: %s' % (time.time(),str)
#===============================================================================
#    this function executes a command on the host using os.popen, and returns all lines
#===============================================================================
    def _exec(self, cmd):
        self.verbose('_exec(%s)' % (cmd))
        prg = os.popen(cmd,"r")
        str = ''
        for line in prg.readlines():
            str += line

        return str.rstrip('\n')
#===============================================================================
#    this function will display a progress bar for use in the cli, 
#    this is not intellegent about the current terminal size however, so rendering errors may occur at lower resolutions
#===============================================================================
    def progressbar(self,cper,clen):
        
        str = '['
        it = 100/clen
        offset = 0
        while offset < 100:
            if offset >= cper:
                str = '%s ' % str
            else:
                str = '%s=' % str
            offset += it
            
        str = '%s]' % str
        return str

#===============================================================================
# Manifest generator function, traverses the provided path to provide a manifest file,    
#===============================================================================
    def manifest(self,path):
        from os.path import join, getsize
        cfiles = 0
                
        if os.path.isdir(path):
            mname = '%s.manifest' % time.strftime('%d-%B-%Y',time.gmtime())
            of = file(mname, 'w+')
            for root, dirs, files in os.walk(path):
                self.progress('Please wait, getting initial file count (%s) ...' % (cfiles))
                #get count first loop
                for fname in files:
                    cfiles += 1
            print
            
            q = 'There are currently %s files in %s, do you want to proceed with the manifest?:' % (cfiles,path)
            a = raw_input(q)
            while a not in ('y','n'):
                q = 'Invalid response (y/n):'
                a = raw_input(q)
            if a == 'n':
                sysexit()
            else:
                print
                tfiles = cfiles
                cfiles = 0
                ltime = 0
                lfiles = 0
                filessec = 0
                for root, dirs, files in os.walk(path):  
                    for fname in files:
                        ctime = time.time()
                        if (ctime - ltime) >= 1:
                            if ltime > 0:
                                filessec = round((cfiles - lfiles) / (ctime - ltime),2)
                            ltime = ctime
                            lfiles = cfiles
                        fpath = join(root,fname)
                        hash = self._checksum(fpath)['md5']
                        of.write("%s  %s\n" % (hash, fpath))
                        cfiles += 1
                        fper = round(((1.00*cfiles)/(1.00*tfiles))*100.00,2)
                        self.progress('Added %s/%s Files to manifest (%s%%) (%s/s)' % (cfiles,tfiles,fper,filessec))
            print
            opts.slen = 0
                        
        elif os.path.isfile(path):
            
            mcount = 0
            #get manifest linecount
            for line in open(path,'r'):
                mcount += 1
                self.progress('Please wait getting manifest count (%s)' % (mcount))
            print
            print 'Manifest count complete'
            
            if mcount == 0:
                self.error('Counted 0 lines in manifest ... aborting')
            
            vcount = 0
            #verify manifest
            for line in open(path,'r'):
                vcount += 1
                vper = round(((1.00*vcount)/(1.00*mcount))*100.00,2)
                self.progress('Please wait verifying manifest (%s%%)' % (vper))
                md5 = line[:32]
                mpath = line[34:]
                mpath = mpath.replace("\n",'')
                if len(md5) != 32:
                    self.error('Manifest Verification error line %s md5 is invalid' % vcount,False)
                elif not os.path.isfile(mpath):
                    self.error('Manifest Verification error line %s path is invalid (file may be missing)' % vcount,False)
            print
            print 'Manifest verification complete'            
                        
            vcount = 0
            fcount = 0
            pcount = 0
            failed = []
            filessec = 0
            lfiles = 0
            ltime = 0
            lstr = 0
            for line in open(path,'r'):
                ctime = time.time()
                if (ctime - ltime) >= 1:
                    if ltime > 0:
                        filessec = round((vcount - lfiles) / (ctime - ltime),2)
                    ltime = ctime
                    lfiles = vcount
                md5 = line[:32]
                mpath = line[34:]
                mpath = mpath.replace("\n",'')
                if self._checksum(mpath)['md5'] == md5:
                    pcount += 1
                else:
                    fcount += 1
                    failed.append(mpath)
                vcount += 1
                vper = round(((1.00*vcount)/(1.00*mcount))*100.00,2)
                fper = round(((1.00*fcount)/(1.00*mcount))*100.00,2)
                pper = round(((1.00*pcount)/(1.00*mcount))*100.00,2)
                bar = self.progressbar(vper, 50)
                                
                #[==================================================] Pass (00%) Fail(00%)
                
                str = 'Verification in progress: %s - %s%% Pass(%s%%) Fail(%s%%) %s/s' % (bar,vper,pper,fper,filessec)
                self.progress(str)
            print
            if fcount > 0:
                print '--- START FAILED LIST ---'
                for f in failed:
                    print f
                print '--- END FAIL LIST ---'
    
#===============================================================================
#    Translation of dbstat.php grom the adimpleo project.
#    thanks to: Trent Hornibrook (http://mysqldbahelp.com/) for technical input for dbstat.php
#===============================================================================
    def adimpleo(self):
        import getpass
        min_data    = 0     #minimum table size (bytes) to report  
        min_index   = 0.5   #minimum % for index of total table size 1.0 being 100%
        min_frag    = 0.05  #minimum % threshold to alert for table fragmentation 0.05 (5%) recomended.
 
        print 'In order to proceed I will need some more infromation about your mySQL server...'
        print 'This tool does not store your details so you will be prompted each time'
        
        q = 'Please supply username:'
        usr = raw_input(q)
        q = 'Please supply password (Remember to escape any required chars):'
        pwd = getpass.getpass(q)
        q = 'Please supply host:'
        host = raw_input(q)
        mysqlcmd = 'mysql -h %s -u %s -p%s -e' % (host,usr,pwd)
        
        q = 'Stage 1 will analyse your mySQL configuration, do you want to proceed with this step? (y/n):'
        a = raw_input(q)
        while a not in ('y','n'):
            q = 'Invalid input enter y or n:'
            a = raw_input(q)
            
        if a == 'y':
            dbraw = self._exec('%s "show status\g" 2>&1' % (mysqlcmd))
            if re.search('^ERROR',dbraw):
                print 'Failed to connect to mysql with the provided details, error follows...'
                print dbraw
                sys.exit(1)
            lines = re.split('\n',dbraw)
            set = {}
            for line in lines:
                
                res = re.split('([a-zA-Z_]+)\t([0-9]+)',line.strip())
                #buggered if I know why this returning a 4 part array
                if len(res) == 4:
                    set.update({res[1]:res[2]})
                           
            print '--- Report for %s ---' % host
            #threading stats
            #connection stats
            #memory stats
            #query cache
            
            if int(set['Qcache_total_blocks']) > 0:
                #int conversions
                set['Qcache_free_blocks'] = int(set['Qcache_free_blocks'])*1.00
                set['Qcache_free_memory'] = int(set['Qcache_free_memory'])*1.00
                set['Qcache_hits'] = int(set['Qcache_hits'])*1.00
                set['Com_select'] = int(set['Com_select'])*1.00
                set['Com_insert'] = int(set['Com_insert'])*1.00
                set['Com_delete'] = int(set['Com_delete'])*1.00
                set['Com_update'] = int(set['Com_update'])*1.00
                set['Com_replace'] = int(set['Com_replace'])*1.00
                
                #in mySQL 5.1.31 the var Queries appears
                # this is a workaround
                
                #

#===============================================================================
# http://dev.mysql.com/doc/refman/5.1/en/server-status-variables.html#statvar_Queries
# Queries
# 
# The number of statements executed by the server. This variable includes statements executed within stored programs, unlike the Questions variable. This variable was added in MySQL 5.1.31.
# #
# 
# Questions
# 
# The number of statements executed by the server. As of MySQL 5.1.31, this includes only statements sent to the server by clients and no longer includes statements executed within stored programs, unlike the Queries variable.
#===============================================================================

                try:
                    set['Queries'] = int(set['Queries'])*1.00
                    set['Questions'] = int(set['Questions'])*1.00
                    set['Questions'] += set['Queries']
                except:
                    set['Questions'] = int(set['Questions'])*1.00
                            
                Qfrag = round(set['Qcache_free_blocks']/set['Qcache_free_memory']*100.00,2)
                """Query Cache efficiency would be Qcache_hits/(Com_select+Qcache_hits). 
                As you can see we have to add Qcache_hits to Com_select to get total number of queries as if query cache hit happens Com_select is not incremented.
                src: http://www.mysqlperformanceblog.com/2006/07/27/mysql-query-cache/
                
                note: basically says the amount of time the cache is hit for queries that can be cached
                """
                Qeff = round(set['Qcache_hits']/(set['Com_select']+set['Qcache_hits'])*100.00,2)
                #----------------------------------------------------------- """
                #----------------- Query hit %  = Queries - Non cacheable / hits
#------------------------------------------------------------------------------ 
                # Note: basically the amount of times the cache is used in comparrision to the total queries
                #----------------------------------------------------------- """
                # Qhit = round((set['Questions'] - (set['Com_insert']+set['Com_delete']+set['Com_update']+set['Com_replace']))/set['Qcache_hits']*100.00,2)
                
                
                if Qfrag > min_frag*100:
                    print '[!!] Query cache is %s%% fragmented' % Qfrag
                    print '[--] You can run "FLUSH QUERY CACHE" to purge your cache'
                else:
                    print '[--] Query cache is %s%% fragmented' % Qfrag
                               
                if Qeff >= 85 and Qeff <= 95:
                    print '[!-] Query cache efficiency is %s%%' % Qeff
                    print '[--] Consider raising your query_cache_size'
                elif Qeff < 85:
                    print '[!!] Query cache efficiency is %s%%' % Qeff
                    print '[--] Consider raising your query_cache_size'
                else:
                    print '[--] Query cache efficiency is %s%%' % Qeff
                    print '[--] Your query cache settings are fine'
                    
                print '[--] The cache efficiency is the cache hits / (cache hits + cache misses)'
                
                
            else:
                print '[!!] Query cache is not enabled'
            #joins stats
            #open file stats
            #table cache
            #temp tables
            #lock:wait
            print '--- END Report for %s ---' % host
            
            
        print 'Stage 2 will analyse a specific database on the server'
        
        dbraw = self._exec('%s "show databases\g" 2>&1' % (mysqlcmd))
        
        if re.search('^ERROR',dbraw):
            print 'Failed to connect to mysql with the provided details, error follows...'
            print dbraw
            sys.exit(1)
        else:
            dbs = re.split('\n', dbraw)
            # 0 - Is always the header we can skip over it
            del dbs[0]
            
            print 'I found %s Databases, please select the one to report on' % len(dbs)
            print
            
            
            index = 0
            for db in dbs:
                print '%s)'%index,db
                index += 1
                
            q = 'Please enter number (q to quit): '
            a = raw_input(q)
            
            if a != 'q':
                a = int(a)
                
            while a not in range(len(dbs)+1) and a != 'q':
                 q = 'Invalid selection (enter q to quit):'
                 a = raw_input(q)
                 if a != 'q':
                    a = int(a)

            if a == 'q':
                sysexit()

            #if we haven't exised we are continuing!
            
            olda = a
            q = 'You have selected %s please choose report type (warn/full):' % dbs[a]
            rdb = a
            a = raw_input(q)

            while a not in ('warn','full','q'):
                q = 'Invalid selection (enter q to quit):'
                a = raw_input(q)
                if a == 'q':
                    sysexit()
            
            type = a
            
            a = olda
            
            # tables
            sql =   '"select table_name, engine, data_length, index_length, (data_length + index_length) as total_length, ' \
                    'table_rows, data_free, update_time from information_schema.tables where engine is not null and table_schema=\'%s\' order by total_length desc\g" 2>&1' % dbs[a]
                    
            dbraw = self._exec('%s %s' % (mysqlcmd,sql))
            
            if re.search('^ERROR',dbraw):
                print 'Failed to get data, error follows ...'
                print dbraw
                sysexit()
            
            lines = re.split('\n',dbraw)
            #0 = headers
            del lines[0]
            
            print '--- Report for %s ---' % dbs[a]
            for line in lines:
                #0 - table_name
                #1 - engine
                #2 - data length
                #3 - index length
                #4 - total length
                #5 - total rows
                #6 - data_free
                #7 - update_time part1
                #8 - update_time part 2
                dat = re.split('\s+',line)
                
                print '-- %s' % dat[0]
                
                #data_length checks
                if int(dat[2]) <= min_data:
                    print '[!!] DATA_LENGTH %s <= %s' % (dat[2],min_data)
                elif type == 'full':
                    print '[--] DATA_LENGTH = %s' % dat[2]
                index_ratio = float(dat[3])/float(dat[4])
                #index_ratio checks
                if index_ratio > min_index:
                    print '[!!] INDEX_LENGTH:TOTAL_LENGTH Ratio %s > %s' % (index_ratio,min_index)
                elif index_ratio < min_index:
                    print '[!!] INDEX_LENGTH:TOTAL_LENGTH Ratio %s < %s' % (index_ratio,min_index)
                elif type == 'full':
                    print '[--] INDEX_LENGTH:TOTAL_LENGTH Ratio = %s' % index_ratio
                #fragmentation checks
                frag_ratio = float(dat[6])/float(dat[4])
                if frag_ratio > min_frag:
                    print '[!!] Table is above threshold fragmented %s%%' % (frag_ratio * 100.00)
                elif type == 'full':
                    print '[--] Table fragmentation below threshold currently %s%%' %  (frag_ratio * 100.00)
                    
                #general information
                if type == 'full':
                    print '[--] TOTAL_LENGTH = %sMB' % round(float(float(dat[4])/1024/1024),2)
                    print '[--] TOTAL_ROWS = %s' % dat[5]
                    print '[--] UPDATE_TIME = %s %s' % (dat[7],dat[8])
                
                print '--- END Report for %s ---' % dbs[a]
    
    def sslinfo(self,opts):
       print 'coming soon...'

    def lbcheck(self):
        print 'This function uses sockets to query each server in the list provided and compare the returned html'
        print 'you will need to provide the server name, list of comma seperated ip\'s for comparrison and the URI'
        print 'each server will need to be addressable from your current location for the tests to complete'
        print 'NOTE: if your web app is designed to render dynamic content the hashes will allways be different'
        print 
        servername = raw_input('server name (www.domain.com): ')
        uri = raw_input('URI: ')
        hosts =  raw_input('ip list: ')
        hosts = hosts.split(',')
        res = {}
        #--------------------------------------------------------- import socket
        import httplib
        #loop list getting data
        for host in hosts:
            conn = httplib.HTTPConnection(host)
            headers = {"host":servername}
            conn.request("GET",uri,{},headers)
            resp = conn.getresponse()
            data = resp.read()
            #res.update({host:{'data':data,'hash':self._checksum(data),'code':re.split('HTTP/1\.1 ([0-9]+)',data)[1]}})
            #------------- s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #---------------------------------------------- s.connect((host,80))
            #------------------------------- s.send("GET %s HTTP/1.1\n" % (uri))
            #------------------------------- s.send("host: %s\n" % (servername))
            #------------------------------------------------------ s.send("\n")
            #--------------------------------------------------------- data = ''
            #------------------------------------------------ tmp = s.recv(1024)
            #----------------------------------------------- while len(tmp) > 0:
                #------------------------------------ data = '%s%s' % (data,tmp)
                #-------------------------------------------- tmp = s.recv(1024)
            #--------------------------------------------------------- s.close()
#------------------------------------------------------------------------------ 
            # res.update({host:{'data':data,'hash':self._checksum(data),'code':re.split('HTTP/1\.1 ([0-9]+)',data)[1]}})
#------------------------------------------------------------------------------ 
        #------------------------------- html = re.split('<!DOCTYPE|<html',data)
        #------------------------------------------------------- print len(html)
#------------------------------------------------------------------------------ 
        #----------------------------------------------------- #comparision loop
        #---------------------------------------------------- for host in hosts:
            print 'HTTP',resp.status,'HASH',self._checksum(data)['md5'],host
            
            
        
        
        
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
            sysexit()
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

class opts:
    slen = 0
    exit = False
    
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
        
        windowsreturn - This command will remove all \\r (^M) chars from a file, windows typically uses \\r\\n for carriage returns, this causes issues particularly when used in bash scripts
        Example: -c windowsreturn -d /path/to/file
        Notes: This will overwrite the original file, as such make sure you have a backup
        
        manifest (BETA) - This command will attempt to iterate the given path and generate an md5 manifest file for all files in that path and it's subdirectories, or verify an existing manifest
        Example: -c manifest -d /path/to/folder
        Example: -c manifest -d /path/to/existing.manifest
        Notes: If bulding a new manifest this will write out a dd-Mon-YYYY.manifest file in your CWD (current working directory) so make sure you are not in the path you are indexing!
        
        adimpleo (BETA) - This command runs analytics against a mySQL server, no credentials are stored you will be prompted at runtime
        Example: -c adimpleo
        Notes: no -d flag is required, this is for security to prevent passwords showing up in shell history
                
        
    """ % (sys.argv[0])
    
    return help

def crashdump():
    #only crash dump if unexpected exit
    if opts.exit == False:
        print 'Opps! something went wrong, please forward the below to d.busby@saiweb.co.uk'
        
        print '--- BEGIN DUMP ---'
        cla, exc, trbk = sys.exc_info()
        excName = cla.__name__
        try:
            excArgs = exc.__dict__["args"]
        except KeyError:
            excArgs = "<no args>"
        excTb = traceback.format_tb(trbk, 5)
        
        str = ''
        for line in excTb:
            str = '%s%s' % (str,line)
        dump = """
     Error: %s
     Args: %s
     Trace:
        
     %s
        """ % (excName,excArgs,str)
        import base64
        
        #dump = base64.b64encode(dump)               
        print dump
        print '--- END DUMP ---'

def main():
    try:
        sa = sysadmin()
        sa.verbose('main()')         
        parser = OptionParser(usage=usage(), version="%prog 1.0")
        parser.add_option('-c','--command', dest='command', help='Command to run')
        parser.add_option('-d','--data', dest='data', help='CSV Style data')
        
        (options,args) = parser.parse_args()
        
        sa.verbose('args parsed')
        
        # excluded from required data list
        edlist = ('adimpleo','lbcheck')
        
        if options.command == None:
            print usage()
            print 'Command is a required input'
            sysexit()
        elif options.data == None and options.command not in edlist:
            print usage()
            print 'Data is a required input'
            sysexit()
        else:
            sa.verbose('Command: %s' % (options.command))
            
            if options.command not in edlist:
                opts = options.data.split(',')
            
            #todo: replace this, couldn't get switch statements working properly!
            if options.command == 'iconv':
                sa._iconv(opts)
            elif options.command == 'appmem':
                sa.appmem(opts[0])
            elif options.command == 'checksum':
                sa.checksum(opts[0])
            elif options.command == 'rblcheck':
                sa.rblcheck(opts)
            elif options.command == 'httpd_stats':
                sa.httpd_stats(opts)
            elif options.command == 'windowsreturn':
                sa.windowsreturn(opts[0])
            elif options.command == 'fscompare':
                sa.filesystem_compare(opts)
            elif options.command == 'manifest':
                sa.manifest(opts[0])
            elif options.command == 'adimpleo':
                sa.adimpleo()
            elif options.command == 'lbcheck':
                sa.lbcheck()
            else:
                print 'Command not found "%s"' % (options.command)
    except:
        crashdump()
 
def sysexit(ret=0):
    opts.exit = True
    sys.exit(ret)      
 #===============================================================================
# signal handler
#===============================================================================
def signals():
    signal(SIGTERM,sighandler)
    signal(SIGINT,sighandler)
#===============================================================================
# signal handler callback
#===============================================================================
def sighandler(signum,frame):
    if signum == SIGINT:
        
        print
        print 'Got ^C Aborting ...'
        sysexit(1)
       
                
if __name__ == "__main__":
    signals()
    main()

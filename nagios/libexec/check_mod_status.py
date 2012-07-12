#!/usr/local/bin/python
#
#  check_mod_status.py
#  
#  Created by David Busby on 30/03/2009.
#
"""
__author__="David Busby"
__copyright__="Psycle Interactive Ltd & David Busby"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
"""

#imports
import sys, getopt, httplib, string, urllib2, re
#global vars
TAG="HTTPD_STATUS"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:c:w:d:x:", ["help", "output="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)           
    srv = ""        #server to read status from
    cpuc = 0       #cpu critical threshold
    cpuw = 0       #cpu warning threshold
    freec = 0      #free slot warning threshold
    freew = 0      #free slot warning threshold
    
    for o, a in opts:
        if o in ("-h", "--help"):
           usage()
        elif o == "-s":
           srv = a
        elif o == "-c":
            cpuc = a
        elif o == "-w":
            cpuw = a
        elif o == "-d":
            freec = int(a)
        elif o == "-x":
            freew = int(a)
        else:
            assert False, "unhandled option"
    
    if len(srv) > 0 and cpuc > 0 and cpuw > 0 and freec > 0 and freew > 0:
        
        srv = "%s%s%s" % ("http://",srv,"/server-status?auto")
        
        req = urllib2.Request(srv)
        try:
           res = urllib2.urlopen(req)
           headers = res.info().headers
           data = res.read()
        except IOError, e:
            if hasattr(e, 'reason'):
                critical(e.reason)
            elif hasattr(e, 'code'):
                critical(e.code)        
        
        if len(data) > 0:
	    #data = data.split("\n")
            #the following does assume however that the auto data provides the following order
            # 
            #
            # Total Accesses: 39186
            # Total kBytes: 2168752
            # CPULoad: 1.16224
            # Uptime: 34923
            # ReqPerSec: 1.12207
            # BytesPerSec: 63591.4
            # BytesPerReq: 56673.4
            # BusyWorkers: 1
            # IdleWorkers: 19
            # Scoreboard:
            
            #total accesses
            #adata = {
            #         "ta":      data[0].split(":")[1].lstrip(),
            #         "tk":      data[1].split(":")[1].lstrip(),
            #         "cpu":     float(data[2].split(":")[1].lstrip()),
            #         "up":      data[3].split(":")[1].lstrip(),
            #         "rps":     data[4].split(":")[1].lstrip(),
            #         "bps":     data[5].split(":")[1].lstrip(),
            #         "bpr":     data[6].split(":")[1].lstrip(),
            #         "bw":      data[7].split(":")[1].lstrip(),
            #         "iw":      data[8].split(":")[1].lstrip(),
            #         "sb":      data[9].split(":")[1].lstrip()
            #}
            
	    #Regex Data cap

	    adata = {
                     "ta":      0 if re.search('Total\sAccesses:\s+([0-9]+)',data) == None else re.search('Total\sAccesses:\s+([0-9]+)',data).group(1),
                     "tk":      0 if re.search('Total\skBytes:\s+([0-9]+)',data) == None else re.search('Total\skBytes:\s+([0-9]+)',data).group(1),
                     "cpu":     float(0 if re.search('CPULoad:\s+([0-9]+\.?[0-9]+)',data) == None else re.search('CPULoad:\s+([0-9]+\.?[0-9]+)',data).group(1)),
                     "up":      0 if re.search('Uptime:\s+([0-9]+)',data) == None else re.search('Uptime:\s+([0-9]+)',data).group(1),
                     "rps":     0 if re.search('ReqPerSec:\s+([0-9]+)',data) == None else re.search('ReqPerSec:\s+([0-9]+)',data).group(1),
                     "bps":     0 if re.search('BytesPerSec:\s+([0-9]+\.?[0-9]+)',data) == None else re.search('BytesPerSec:\s+([0-9]+\.?[0-9]+)',data).group(1),
                     "bpr":     0 if re.search('BytesPerReq:\s+([0-9]+\.?[0-9]+)',data) == None else re.search('BytesPerReq:\s+([0-9]+\.?[0-9]+)',data).group(1), 
                     "bw":      0 if re.search('BusyWorkers:\s+([0-9]+)',data) == None else re.search('BusyWorkers:\s+([0-9]+)',data).group(1),
                     "iw":      0 if re.search('IdleWorkers:\s+([0-9]+)',data) == None else re.search('IdleWorkers:\s+([0-9]+)',data).group(1),
                     "sb":      '' if re.search('Scoreboard:\s+(.*)',data) == None else re.search('Scoreboard:\s+(.*)',data).group(1)
            }
            #parse the score board
            asb = sb_parse(adata["sb"])
            #generate perfdata
            stat ="| cpu_load=%s;0; max=%s;0; waiting=%s;0; starting=%s;0;" % (adata["cpu"], asb["max"], asb["wc"], asb["su"])
            stat = stat +" reading=%s;0; sending=%s;0; keepalive=%s;0; lookup=%s;0;"  % (asb["rr"], asb["sr"], asb["ka"], asb["dns"])
            stat = stat +" closing=%s;0; logging=%s;0; finishing=%s;0; idle=%s;0;"  % (asb["cc"], asb["lo"], asb["gf"], asb["id"])
            stat = stat + " open=%s;0; bytes_per_sec=%s;0; Uptime=%s;0; total_accesses=%s;0;"  % (asb["op"], adata["bps"], adata["up"], adata["ta"])          
            
            #check cpu load
            if adata["cpu"] >= cpuc:
                critical("CPULoad Percentage: %s exceeds critical threshold (%s)%s" % (adata["cpu"],cpuc,stat))
            elif adata["cpu"] >= cpuw:
                warn("CPULoad Percentage: %s exceeds warning threshold (%s)%s" % (adata["cpu"],cpuw,stat))
            #free slot check
            perfree = (1.0*asb["op"]/asb["max"])*100
                       
            if perfree <= freec:
                critical("Free Slots Percentage: %s less than critical threshold (%s)%s" % (perfree,freec,stat))
            elif perfree <= freew:
                warn("Free Slots Percentage: %s less than warning threshold (%s)%s" % (perfree,freew,stat))
                
            #no of the checks have caused an exit so status is ok!
            ok("CPU: %s FREE: %s %s" % (adata["cpu"],perfree,stat))
        else:
            stat = "No Data"
            critical(stat)
    else:
        usage()

def sb_parse(sb):
    #setup struct / assoc array
    asb = {
           "wc": 0, #"_" Waiting for Connection
           "su": 0, #"S" Starting up
           "rr": 0, #"R" Reading Request
           "sr": 0, #"W" Sending Reply
           "ka": 0, #"K" Keepalive (read) 
           "dns": 0, #"D" DNS Lookup,
           "cc": 0, #"C" Closing connection
           "lo": 0, #"L" Logging
           "gf": 0, #"G" Gracefully finishing
           "id": 0, #"I" Idle cleanup of worker
           "op": 0, #"." Open slot with no current process
           "max": 0 #max slots
        }
    sblen = len(sb)
    asb["max"] = sblen
    for i in range(0,sblen):
        if sb[i] == "_":
            asb["wc"] += 1
        elif sb[i] == "S":
            asb["su"] += 1
        elif sb[i] == "R":
            asb["rr"] += 1
        elif sb[i] == "W":
            asb["sr"] += 1
        elif sb[i] == "K":
            asb["ka"] += 1
        elif sb[i] == "D":
            asb["dns"] += 1
        elif sb[i] == "C":
            asb["cc"] += 1
        elif sb[i] == "L":
            asb["lo"] += 1
        elif sb[i] == "G":
            asb["gf"] += 1
        elif sb[i] == "I":
            asb["id"] += 1
        elif sb[i] == ".":
            asb["op"] += 1
    
    return asb
 
def usage():
    print "Usage: ",sys.argv[0]," [-h][-s][-c][-w][-d][-x]"
    print "-s server_ip or name"
    print "-c critical CPU max percentage"
    print "-w warning CPU max percentage"
    print "-d critical free slot min percentage"
    print "-x warning free slot min percentage"
    print "NOTE: DO NOT include the http:// or /server-status?auto in the server address."
    sys.exit(0)

def ok(stat):
    print TAG,"OK -",stat
    sys.exit(0)
    
def warn(stat):
    print TAG,"WARN -",stat
    sys.exit(1)
    
def critical(stat):
    print TAG,"CRITICAL -",stat
    sys.exit(2);
    
if __name__ == "__main__":
    main()

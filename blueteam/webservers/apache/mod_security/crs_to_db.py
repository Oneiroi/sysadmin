#!/usr/bin/env python
import sys
import optparse
from time import time
import re

'''
__author__="David Busby"
__copyright__="David Busby <d.busby@saiweb.co.uk> & Psycle Interactive Ltd"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
'''

'''
This code adapted from https://github.com/Oneiroi/PenTesting/tree/master/crypto/generators/mysql csv_gen.py
'''

class opts:
    slen = 0

def usage():
	print sys.argv[0],'-d /path/to/crs_dir -f <output format sqlite,mysql>  -t <max threads, default 1>'
    print 'Note: whilst mapping to appropriate format from files is multi threaded, writing to the database is not, to avoid lock contention, this may change in the future'

def _crs_to_dict(fPath,r):
    if os.path.isfile(fPath):
        
def main():
	try:
		opts,args = getopt.getopt(sys.argv[1:],'f:o:t:l',[])
	except getopt.GetoptError, e:
		print e
		usage()
		sys.exit(2)
	
	wlist   = None
	ofile   = None
	threads = 2
	legacy = False
	for o,a in opts:
		if o == '-f':
			wlist = a
		elif o == '-o':
			ofile = a
                elif o == '-t':
                        threads = int(a)
		elif o == '-l':
			legacy = True
                else:
                    assert False,'Unsupported option %s' %a
	
	if ofile == None:
		print 'Output file not specified, exiting'
		sys.exit(2)
	if wlist == None:
		print 'Wordlist file not specified exiting'
		sys.exit(2)

	p = multiprocessing.Pool(processes=threads)

	i = 0
	words = []
        print 'Please wait getting reading wordlist from %s' %wlist
	for word in open(wlist,'r'):
		words.append(word)
		i+=1
                progress('%d words'%i)

	print 'Got %d words from file, processing' % i
	sTime = time()
	if legacy == False:
		data = p.map(hash,words)
	else:
		data = p.map(old_hash,words)

	eTime = time()
	print 'Completed hashing of %d words in %.2f seconds (%.2f/s) using %d threads' % (i,(eTime-sTime),(i/(eTime-sTime)),threads)
	
	f = open(ofile,'w+')
	for dict in data:
		for hashmap in dict:
			str = '%s,%s' % (hashmap,dict[hashmap])
			f.write(str)
	f.close()
	
	print 'csv format is complete %s' %ofile

if __name__ == '__main__':
	main()

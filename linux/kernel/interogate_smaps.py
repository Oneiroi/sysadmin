#!/usr/bin/env python
import glob

def main():
  template = '{0:10}'
  for i in xrange(1,14):
    template += '{%d:15}' %i

  print template.format(
      'Process',
      'Size',
      'Rss',
      'Pss',
      'Shared_Clean',
      'Shared_Dirty',
      'Private_Clean',
      'Private_Dirty',
      'Referenced',
      'Anonymous',
      'AnonHugePages',
      'Swap',
      'KernelPageSize',
      'MMUPageSize')

  smaps = glob.glob('/proc/[0-9]*/smaps')
   
if __name__ == '__main__':
  main()

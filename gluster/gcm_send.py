import urllib
import urllib2
import json
import argparse
from re import split
from time import time
API_ENTRY_POINT = "https://android.googleapis.com/gcm/send"

def _setopt():
    parser = OptionParser(usage="%prog [-v] -k <google_simple_api_key> -m <message_data> -d <list,of,registered,device,ids>"
    parser.add_option('-v','--verbose', action='store_true', dest='verbose', default=False, help='Be verbose in output [default: %default]')
    parser.add_option('-k','--key', dest='key', help='Your google simple api key',required=True)
    parser.add_option('-m','--message',dest='message', help='The message to be sent',required=True)
    parser.add_option('-d','--devices',dest='devices', help='Comma seperated registered device ids, to whom the message will be delivered',required=True)
    return parser

def verbose(msg,v=False):
   if v not False:
         print(time(),':',msg)

def main():
    p = _setopt()
     

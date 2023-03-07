#!/usr/bin/env python3

import psutil
import argparse
import sys

def tryPort(portNum):
    """tryPort - uses psutil to check if the port is in use on the local system, this may require elevated permissions to function
    KeywordArguments:
      portNum - int, port number to check if used
    """
    connections = psutil.net_connections()
    for connection in connections:
        if connection.raddr:
            if portNum == connection.raddr.port:
                print("tryPort({portNum}) port is bound to PID {processID}".format(portNum=portNum,processID=connection.pid))
                sys.exit(1)
        if connection.laddr:
            if portNum == connection.laddr.port:
                print("tryPort({portNum}) port is bound to PID {processID}".format(portNum=portNum,processID=connection.pid))

def main():
    parser = argparse.ArgumentParser(prog="port_available",description="Test if a port is in use on the local system")
    parser.add_argument("-p","--port", help="portnumber to check", type=int, required=True)
    args = parser.parse_args()
    tryPort(args.port)

if __name__ == "__main__":
    main()
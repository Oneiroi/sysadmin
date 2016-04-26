#!/bin/bash
iptables -N TOR
iptables -I INPUT -j TOR
curl https://check.torproject.org/exit-addresses | grep ExitAddress | awk '{print $2}' |  sort  | awk '{print "iptables -I TOR -s "$1" -j DROP"}'

#!/bin/bash
echo "#[NOOP] No actions will be taken on your system, you will need to copy & paste this output"
echo "iptables -N TOR"
echo "iptables -I INPUT -j TOR"
curl -s https://check.torproject.org/exit-addresses | grep ExitAddress | awk '{print $2}' |  sort  | awk '{print "iptables -I TOR -s "$1" -j DROP"}'

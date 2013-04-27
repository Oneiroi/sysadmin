#!/bin/bash

#################################################################
#				~~ sysadmin script ~~~							#
#				~~ Saiweb.co.uk ~~								#
#																#
# http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA	#												#
# Copyright 2008 D.Busby										#
#################################################################

#CONFIG

#Change this for your local IP you listening for connections on
LOCAL_IP="123.456.789.123";

#IP Scan vars
#ips start
IPS_START=1;
#ips end
IPS_END=254;
#range prefix
IPS_RANGE="192.168.1.";

#END CONFIG

function appmem {
	if [ -z "$1" ]; then
		echo "Usage: sysadmin appmem app_name i.e. (sysadmin appmem apache)";
	else
		RRES=(`ps aux | grep "$1" | grep -v ‘grep’ | grep -v "$0" | awk '{print $6}'`);
		VRES=(`ps aux | grep "$1" | grep -v ‘grep’ | grep -v "$0" | awk '{print $5}'`);
		COUNT=0;
		VMEM=0;
		RMEM=0;
		for RSS in ${RRES[@]}
		do
			RMEM=$(($RSS+$RMEM));
		done;
		for VIRT in ${VRES[@]}
		do
			VMEM=$(($VIRT+$VMEM));
			COUNT=$(($COUNT+1));
		done;
		VMEM=$(($VMEM/$COUNT));
		VMEM=$(($VMEM/1024));
		RMEM=$(($RMEM/1024));
		echo -e "$YELLOW —– MEMORY USAGE REPORT FOR '$1' —– $CLEAR";
		echo "PID Count: $COUNT";
		echo "Shared Mem usage: $VMEM MB";
		echo "Total Resident Set Size: $RMEM MB";
		echo "Mem/PID: $(($RMEM/$COUNT)) MB";
	fi
}

#ip scan function
function ipscan {
	echo "Now running IPSCAN $IPS_RANGE$IPS_START - $IPS_RANGE$IPS_END"
	for ((i=$IPS_START;i<=$IPS_END;i+=1)); do
		RESULT=`ping -c 1 -t 1 $IPS_RANGE$i | grep "bytes from"`;
		if [ -z "$RESULT" ]; then
			echo -e "$IPS_RANGE$i:$RED DEAD $CLEAR";
			# If you comment out the above to report just the alive hosts, bash gets a bit funny about not processing anything here, so uncomment the below to keep it happy
			#holder=$i;
		else
			MAC=`arp $IPS_RANGE$i | awk ‘{ print $4 }’;`;
			echo -e "$IPS_RANGE$i:$GREEN ALIVE $CLEAR ($MAC)";
		fi
	done
}

#check for port connections by parsing netstat output
function portcon {
echo "----- Active Connections For Port $1 -----";
netstat -ant | grep "$LOCAL_IP:$1 " | wc -l
netstat -ant | grep "$LOCAL_IP:$1 " | awk '{ print $5 }' | awk -F \: '{ print $1 }' | sort | uniq -c | sort -n
}

#colours
function colours {
CLEAR='\e[00m';
GREEN='\e[0;32m';
RED='\e[0;31m';
YELLOW='\e[1;33m';
}

function usage {
	echo "TODO put something here";
}

if [ -z $1 ]; then
	usage;
	exit;
fi

colours;
$1 $2
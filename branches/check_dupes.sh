#!/bin/bash


#################################################################
#				~~ sysadmin script ~~~							#
#				~~ Saiweb.co.uk ~~								#
#																#
# http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA	#												#
# Copyright 2008 D.Busby										#
# I realy wouldn't edit this file, if you bork your DB server	#
# it's your own fault											#
#################################################################

SERV='';
USR='';
PWD='';
TBL='';
FIELD='';

function usage {
	echo "Usage: $0 -s 123.123.123.123 -u user -p password -d database -t table -f field";
	echo "Check for non unique entries on the table in the specified field.";
	echo "If the field in question is not indexed, depending on the row count this check could take a very long time to complete";
	exit 0;
}

function go {
	if [ ! -x '/usr/bin/mysql' ]; then
		echo "Can't find mysql client!";
		exit 0;
	fi
	SQL="'SELECT count($FIELD) as CNT, $FIELD FROM $TABLE GROUP BY $FIELD HAVING CNT > 1\G'";
	#mysql client uses stderr when error occurs. We need the info so 2>&1 redirects stderr to stdout
	CMD=`/usr/bin/mysql -h $SERV -u $USR -p$PWD $DB -e $SQL 2>&1`;
	
	ERR=0;
	ERR=$((`echo "$CMD" | grep "ERROR" | wc -l`));
	
	if [ $ERR -gt 0 ]; then
		echo $CMD;
		exit 0;
	fi;
	
	echo $CMD;
}

while getopts "hs:u:p:t:f:" optionName; do
	case "$optionName" in
		h) usage;;
		s) SERV=$OPTARG;;
		u) USR=$OPTARG;;
		p) PWD=$OPTARG;;
		d) DB=$OPTARG;;
		t) TBL=$OPTARG;;
		f) FIELD=$OPTARG;;
		[?]) usage;;
	esac
done

go;
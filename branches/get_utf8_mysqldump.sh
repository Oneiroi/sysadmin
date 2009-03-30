#!/bin/bash


#################################################################
#				~~ sysadmin script ~~~							#
#				~~ Saiweb.co.uk ~~								#
#																#
# http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA	#												#
# Copyright 2008 D.Busby										#
#################################################################


function usage {
	echo "Usage $0 -s host -u user_name -p password -f /path/to/output.sql";
}

function go {
	MYSQL=$(which mysql);

	if [ ! -x "$MYSQL" ]; then
		echo "Can't find mysql!";
		exit 0;
	fi
	
	MYSQLD=$(which mysqldump);

	if [ ! -x "$MYSQLD" ]; then
		echo "Can't find mysqldump!";
		exit 0;
	fi
	
	#get a list of DB's
	CMD=``;
	
	date +%d-%m-%Y-%H:%M
	
	CMD=`$MYSQL --default-character-set=utf8 --set-charset -h $SRV -u $USR -p$PWD $DB > $FILE`;
	
	
	
}

USR='';
PWD='';
DB='';
FILE='';
SRV='';

while getopts "hs:u:p:d:" optionName; do
        case "$optionName" in
                h) usage;;
                u) USR=$OPTARG;;
                p) PWD=$OPTARG;;
                d) DB=$OPTARG;;
                f) FILE=$OPTARG;;
                s) SRV=$OPTARG;;
                [?]) usage;;
        esac
done

go;
#!/bin/bash

#################################################################
#				~~ sysadmin script ~~~							#
#				~~ Saiweb.co.uk ~~								#
#																#
# http://creativecommons.org/licenses/by-sa/2.0/uk/ CC BY-SA	#												#
# Copyright 2008 D.Busby										#
#################################################################

function usage {
        echo "Usage $0 -f /path/to/access_log.log";
        echo "NOTE: This script does not check for valid apache log syntax, it assumes 'combined' output.";
}

function go {
        if [ $FLAG -lt 1 ]; then
                usage;
                exit 0;
        fi

        if [ ! -f $FILE ]; then
                echo "Failed to open: $FILE";
                exit 0;
        fi

        END=`tail -n 1 $FILE | awk '{print $4$5}';`;
        STA=`head -n 1 $FILE | awk '{print $4$5}';`;

        #cat the file, get just the http code and 'size', grep remove any errant "-" (no data size), return just the file size.
        DARRAY=(`cat $FILE | awk '{print $9,$10}' | grep -v "-" | grep -v "+" | awk '{print $2}';`);
        TOT=0;

        for DAT in ${DARRAY[@]};
        do
                TOT=$(($TOT+$DAT));
        done;


        KB=`echo "$TOT" | awk '{print $1/1024}';`;
        MB=`echo "$KB" | awk '{print $1/1024}';`;
        GB=`echo "$MB" | awk '{print $1/1024}';`;
        echo "Log Range: $STA - $END":
        echo "Total Bytes: $TOT";
        echo "Total KBytes: $KB";
        echo "Total MBytes: $MB";
        echo "Total GBytes: $GB";
}

FILE='';
FLAG=0;
while getopts "hf:" optionName; do
        case "$optionName" in
                h) usage;;
                f) FILE=$OPTARG;FLAG=1;;
                [?]) usage;;
        esac
done

go;

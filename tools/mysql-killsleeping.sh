#!/bin/bash
for (( i=0; i<360; i++ ))
do
        for (( j=10; j>0; j-- ))
        do
                echo -n "$j "
                sleep 1
        done
        
        PIDS=$( mysql -e 'show processlist' | grep Sleep | awk '{print $1}' )
        count=$( mysql -e 'show processlist' | grep Sleep | awk '{print $1}' | wc -l )  
        for pid in $( mysql -e 'show processlist' | grep Sleep | awk '{print $1}' )
        do
                mysql -e "kill $pid";
        done
        echo "Killed $count"
done


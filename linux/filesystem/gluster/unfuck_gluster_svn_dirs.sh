#!/bin/bash
echo "you may want to edit the script and remove the appropriate trusted.afr directories"
[[ ! -d "$1" ]] && echo "Usage: $0 /path/to/filesystem (NOT MOUNTPOINT)" && exit 1;

#pass 1 get .svn dirs and trash attrs
DIRS=`find $1 -type d -iname '.svn'`
for d in ${DIRS[@]}; do
    #setfattr -x trusted.afr.DEV-client-0 $d; 
    #setfattr -x trusted.afr.DEV-client-1 $d;
    setfattr -x trusted.gfid $d
    #find $d -type d -exec setfattr -x trusted.afr.DEV-client-0 {} \;
    #find $d -type d -exec setfattr -x trusted.afr.DEV-client-1 {} \;
    find $d -type d -exec setfattr -x trusted.gfid {} \;
done



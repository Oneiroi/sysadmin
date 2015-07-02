#!/bin/bash

XARGS=`type xargs | awk '{print $3}'`
FIND=`type find | awk '{print $3}'`

echo "[INFO] By Default this uses Xargs to provide multiprocessing where available, this is set to use the maximum available threads, this may not be suitable for production, remove the -P0 option if required"

[[ ! -x "$XARGS" ]] && (echo "I need XARGS TO proceed" && exit 1)
[[ ! -x "$FIND" ]] && (echo "I need FIND TO proceed" && exit 1)
[[ ! -d "$1" ]] && (echo "Usage: $0 /path/to/start/dir" && exit 1)
TMP=`mktemp -d`

echo '[INFO] Producing filelist *.php > $TMP/files'
find $1 -noleaf -type f -name '*.php' -print0 > $TMP/files
echo '[INFO] Completed $TMP/files'
echo '[HIGH] Search for high likelyhood compromises'
cat $TMP/files | xargs --null -P0 egrep -iIH 'eval[[:space:]]+?\([[:space:]]+?(base64|gzinflate|edoced)'
echo '[MEDIUM] PASS 1 - Search for medium likelyhood compromises, may produce a lot of false positives if you frequently use os exec functions legitimately'
cat $TMP/files | xargs --null -P0 egrep -iIH 'ex|exec|passthru|system|pcntl_|proc_|posix_|ssh2_|ssh_'
echo '[MEDIUM] PASS 2 - Search for medium likelyhood compromises, may produce a lot of false positives if you use hex strings legitimately'
cat $TMP/files | xargs --null -P0 egrep -iIH '\x'
echo '[MEDIUM] PASS 3 - Search for medium likelyhood compromises, may produce a lot of false positives if you ord or pack legitimately'
cat $TMP/files | xargs --null -P0 egrep -iIH 'ord|pack[[:space:]]+?\('
echo '[LOW] Search for low likelyhood compromises, may produce a lot of false positives if you use ini_* legitimately'
cat $TMP/files | xargs --null -P0 egrep -iIH 'ini_.*[[:space:]]+?\('



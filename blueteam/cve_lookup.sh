#!/bin/bash

[[ -z "$1" ]] && echo "Usage: $0 CVE-YYYY-NNNN" && exit 1

curl -s http://www.cvedetails.com/cve/$1/ | grep 'meta name="description" content="' | awk -F\" '{print $4}'

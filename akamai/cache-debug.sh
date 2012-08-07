#!/bin/bash

[[ -z "$1" ]] && echo "Usage: $0 http://fqdn.tld/uri/to/test/with/get" && exit 1

curl=`type curl | awk '{print $3}'`

[[ ! -x $curl ]] && echo "Curl could not be found; aborting." && exit 1

$curl -L -o /dev/null -v -s -H 'Pragma: akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-check-cacheable, akamai-x-get-cache-key, akamai-x-get-extracted-values, akamai-x-get-nonces, akamai-x-get-ssl-client-session-id, akamai-x-get-true-cache-key, akamai-x-serial-no' $1

#!/usr/bin/env python
# saiweb.co.uk payload unpack script 26/05/2010
# copy the eval(gzinflate()) line to payload.raw, place in same directory as this file.

"""
Copyright (C) 2010 Buzz saiweb.co.uk.co.uk

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    Additional Terms as Per section 7

    Attribution:

    Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form.
"""

import base64, zlib, re, sys

def main():
    print 'Running ...'
    f = open('payload.raw')
    php = f.read()
    f.close()
    iteration = 0
    while re.search('eval\\(base64_decode\(\'',php):
        iteration += 1
        print 'Iteration: %d' % iteration
        raw = re.sub('eval\\(base64_decode\(\'','',php)
        raw = re.sub('\'\)\);','',raw)
        
        php = base64.b64decode(raw.strip())
        #php = zlib.decompressobj().decompress('x\x9c' + gstring)
        #print payload
        #sys.exit()
    print php
if __name__ == '__main__':
    main()


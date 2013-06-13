# validation.py - validation functions for entity models
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
import re

def validate_server(server):
    errors = []

    if not server.hostname:
        errors.append('Hostname must not be empty.')

    if server.port is not None and (server.port < 1 or server.port > 65535):
        errors.append('Port has to be an integer between 1 and 65535 if set.')

    if server.user and re.search('[@\s]', server.user):
        errors.append('Username must not include @-signs or whitespace.')

    if (server.gateway and
        not re.match('^([^@:\s]+@)?([^@:\s]+)(:\d+)?$', server.gateway)):
        errors.append('Gateway must be given in format "user@host:port". '
                      'User and port are optional.')

    return errors

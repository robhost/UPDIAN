# fabric_utils.py - fabric utility functions for updian
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
'''Utility functions for handling updian's data structures'''

import fabric.api

def backend_mapping_generator(serverlist):
    '''Generator yielding pairs of server hostnames and backends.'''
    for server in serverlist:
        yield (server.hostname,
               server.backend or server.defaults['backend'])

class UnknownBackendError(Exception):
    '''Raised when an unsupported backend is used.'''
    def __init__(self, backend):
        super().__init__('Unkown backend: %s' % backend)

def update_check(backend, use_sudo=False):
    '''
    Check for available package updates using the specified backend.

    When use_sudo is True (default=False) sudo is used to start the
    specified backend.

    '''
    driver = fabric.api.sudo if use_sudo else fabric.api.run

    if backend == 'apt':
        driver('DEBIAN_FRONTEND=noninteractive apt-get update -qq', quiet=True)
        with fabric.api.settings(ok_ret_codes=[0, 1]):
            ret = driver('DEBIAN_FRONTEND=noninteractive '
                         'apt-get upgrade -s | '
                         'grep Inst')
    elif backend == 'yum':
        with fabric.api.settings(ok_ret_codes=[0, 100]):
            ret = driver('yum check-update -q')
    else:
        raise UnknownBackendError(backend)

    return ret

def upgrade_packages(backend, use_sudo=False):
    '''
    Upgrade all packages using the specified backend.

    When use_sudo is True (default=False) sudo is used to start the
    specified backend.

    '''
    driver = fabric.api.sudo if use_sudo else fabric.api.run

    if backend == 'apt':
        command = 'DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade'
    elif backend == 'yum':
        command = 'yum -y update'
    else:
        raise UnknownBackendError(backend)

    return driver(command)

def checkrestart(use_sudo=False):
    '''Issue the checkrestart-command.'''
    driver = fabric.api.sudo if use_sudo else fabric.api.run
    command = 'checkrestart'

    return driver(command)

def make_host_list(serverlist):
    '''Create fabric compatible host list from updian's server list.'''
    host_list = []

    for server in serverlist:
        user = server.user or server.defaults['user']
        port = server.port or server.defaults['port']
        hostspec = '%s@%s:%d' % (user, server.hostname, port)

        host_list.append(hostspec)

    return host_list

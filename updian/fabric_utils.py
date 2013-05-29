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

class UnknownBackendError(Exception):
    '''Raised when an unsupported backend is used.'''
    def __init__(self, backend):
        super().__init__('Unknown backend: %s' % backend)

def _detect_backend():
    '''Detect package management backend.'''
    supported_backends = {
        '/usr/bin/apt-get': None,
        '/usr/bin/yum': None,
    }

    for backend in supported_backends:
        with fabric.api.settings(ok_ret_codes=[0, 1]):
            p = fabric.api.run('test -x %s' % backend, quiet=True)
        supported_backends[backend] = p.return_code

    available_backends = [x for x in supported_backends if
                          supported_backends[x] == 0]

    # shouldn't really happen, but better be safe then sorry
    # as there are things like apt-rpm around
    if len(available_backends) > 1:
        raise RuntimeError('Auto-detection of package manager returned '
                           'ambiguous results. More than one package '
                           'manager found on %s.' % fabric.api.env.host)

    backend = available_backends[0]

    if backend == '/usr/bin/apt-get':
        return 'apt'
    elif backend == '/usr/bin/yum':
        return 'yum'

    return None

def update_check(backend=None, use_sudo=False):
    '''Check for available package updates using the specified backend.

    When use_sudo is True (default=False) sudo is used to start the
    specified backend.
    If backend is None (the default) auto-detection is performed.

    '''
    driver = fabric.api.sudo if use_sudo else fabric.api.run

    if backend is None:
        backend = _detect_backend()

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

def upgrade_packages(backend=None,
                     use_sudo=False,
                     allow_unauthenticated_packages = False):
    '''Upgrade all packages using the specified backend.

    When use_sudo is True (default=False) sudo is used to start the
    specified backend.
    If backend is None (the default) auto-detection is performed.

    '''
    driver = fabric.api.sudo if use_sudo else fabric.api.run

    if backend is None:
        backend = _detect_backend()

    if backend == 'apt':
        command = ('PAGER=cat DEBIAN_FRONTEND=noninteractive '
                   'apt-get --yes '
                   '-o Dpkg::Options::="--force-confdef" '
                   '-o Dpkg::Options::="--force-confold" upgrade')
        if allow_unauthenticated_packages:
            command += ' --allow-unauthenticated '
    elif backend == 'yum':
        command = 'yum -y update'
    else:
        raise UnknownBackendError(backend)

    return driver(command, pty=False)

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

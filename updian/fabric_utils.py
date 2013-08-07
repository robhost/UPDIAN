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
    supported_backends = ['/usr/bin/apt-get',
                          '/usr/bin/yum']

    available_backends = [backend for backend in supported_backends if
                          command_is_available(backend)]

    # shouldn't really happen, but better be safe than sorry
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
        driver('/usr/bin/apt-get update -qq', quiet=True)
        ret = driver('/usr/bin/apt-get upgrade -s')

        class ReturnWrapper(object):
            def __init__(self, ret):
                lines = ret.stdout.splitlines(True)
                self.stdout = ''.join([l for l in lines if 'Inst' in l])
                self.subret = ret

            def __getattribute__(self, name):
                try:
                    return object.__getattribute__(self, name)
                except AttributeError:
                    subret = object.__getattribute__(self, 'subret')
                    return getattr(subret, name)

        ret = ReturnWrapper(ret)
    elif backend == 'yum':
        with fabric.api.settings(ok_ret_codes=[0, 100]):
            ret = driver('/usr/bin/yum check-update -q')
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
        args = ['--yes',
                '-o Dpkg::Options::="--force-confdef"',
                '-o Dpkg::Options::="--force-confold"']
        if allow_unauthenticated_packages:
            args.append('--allow-unauthenticated')

        command = 'DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get %s upgrade' % ' '.join(args)
    elif backend == 'yum':
        command = '/usr/bin/yum -y update'
    else:
        raise UnknownBackendError(backend)

    return driver(command, pty=False)

def command_is_available(command):
    '''Check if command is available.'''
    with fabric.api.settings(ok_ret_codes=[0, 1]):
        existence_test = fabric.api.run('test -x %s' % command, quiet=True)

    return existence_test.return_code == 0

def checkrestart(use_sudo=False):
    '''Issue the checkrestart-command.'''
    driver = fabric.api.sudo if use_sudo else fabric.api.run
    command = '/usr/sbin/checkrestart'

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

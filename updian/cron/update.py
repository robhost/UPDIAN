# update.py - cronjob functionality for installing pending updates
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
'''Functions to run updates via updian.'''

from __future__ import print_function

import glob
import os
import random
import time

from fabric.api import parallel, execute, env, settings, hide

from .. import config
from ..fabric_utils import *

__all__ = ['execute_queued_updates']

@parallel(pool_size=config.concurrency)
def do_update(metadata_mapping):
    '''Fabric task that updates packages and logs the output.'''
    metadata = metadata_mapping[env.host]
    backend = metadata.backend
    use_sudo = (env.user != 'root')

    env.gateway = metadata.gateway or metadata.defaults['gateway']

    if backend is None and not config.autodetect_backend:
        backend = metadata.defaults['backend']
        print('No backend given for %s and auto-detection is disabled. '
              'Defaulting to %s' % (env.host, backend))

    print('Host: %s, Port: %s, Engine: %s, Gateway: %s' %
          (env.host, env.port, backend, env.gateway))

    env.shell = '/bin/bash -c'

    s = upgrade_packages(backend, use_sudo,
                         config.allow_unauthenticated_packages)

    log_entry = '{host} ({date}):\n\n{output}\n\n####################\n\n'
    log_entry = log_entry.format(host=env.host,
                                 date=time.strftime('%b %d, %H:%M'),
                                 output=s.stdout.replace('\r', ''))

    logfile = os.path.join(config.log_dir, '%s.log' % env.host)
    with open(logfile, 'a+') as log:
        log.write(log_entry)
    os.chmod(logfile, 0666)

    if backend == 'apt':
        chkrst_res = checkrestart(use_sudo)
        output = chkrst_res.replace('\r', '').strip()

        if output != 'Found 0 processes using old versions of upgraded files':
            chkrst_logfile = '%s_checkrestart.log' % (env.host)
            chkrst_logfile = os.path.join(config.log_dir, chkrst_logfile)
            with open(chkrst_logfile, 'a+') as chkrst_log:
                chkrst_log.write(output)
            os.chmod(chkrst_logfile, 0666)

    queuefile = os.path.join(config.todo_dir, '%s.txt' % env.host)
    os.remove(queuefile)

    datafile = os.path.join(config.data_dir, '%s.txt' % env.host)
    os.remove(datafile)

def execute_queued_updates(serverlist):
    '''Execute updates on all queued hosts (in the todo directory).'''
    todo_files = glob.glob(os.path.join(config.todo_dir, '*.txt'))
    host_queue = [os.path.splitext(os.path.basename(f))[0] for f in todo_files]

    if not host_queue:
        print('No updates in queue (%s) ...' % (time.strftime('%H:%M')))
        return

    serverlist = filter(lambda s: s.hostname in host_queue, serverlist)
    random.shuffle(serverlist)
    metadata_mapping = dict(((s.hostname, s) for s in serverlist))

    with hide('everything'):
        return_vals = execute(do_update,
                              metadata_mapping,
                              hosts=make_host_list(serverlist))

    statfile = os.path.join(config.data_dir, 'statfile_upd')
    open(statfile, 'w').close()

    print('Made %d updates (%s) ...' % (len(serverlist),
                                        time.strftime('%H:%M')))

if __name__ == '__main__':
    from ..serverlist import ServerList

    serverlist = ServerList.from_file(config.serverlist_file)

    execute_queued_updates(serverlist)

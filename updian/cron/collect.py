# collect.py - cronjob functionality for collecting pending updates
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
'''Check hosts for updates and send reports.

Module variables:
    update_mail_subject -- Subject of the summary email. The placeholder
                           `{count}` is replaced with the total update
                           count.
    update_mail_subject -- Body of the summary email. The following
                           placeholders are recognized and replaced:
                             `{count}`:
                                 Total update count.

                             `{update_list}`:
                                 List of update counts per server
                                 separated by line breaks.

                             `{updian_uri}`:
                                 URI of Updian's web-interface as
                                 globally configured.

'''

from __future__ import print_function

import email.mime.text
import glob
import os
import smtplib
import time

from fabric.api import parallel, execute, env, settings, hide

from .. import config
from ..fabric_utils import make_host_list, update_check

__all__ = ['update_mail_subject', 'update_mail_text', 'collect_update_data']

update_mail_subject = '[updian] {count} servers with updates pending!'
update_mail_text = '''
Updian has detected that the following servers have pending updates:

{update_list}

You can manage these updates at {updian_uri}

Regards,
updian on base
'''

@parallel(pool_size=config.concurrency)
def check_for_update(metadata_mapping):
    '''Fabric task that checks hosts for pending updates.'''
    metadata = metadata_mapping[env.host]
    backend = metadata.backend
    use_sudo = (env.user != 'root')

    env.gateway = metadata.gateway or metadata.defaults['gateway']

    if backend is None and not config.autodetect_backend:
        backend = metadata.defaults['backend']
        print('No backend given for %s and auto-detection is disabled. '
              'Defaulting to %s' % (env.host, backend))

    print('Query: %s, Port: %s, Engine: %s, Gateway: %s' %
          (env.host, env.port, backend, env.gateway))

    env.shell = '/bin/bash -c'

    s = update_check(backend, use_sudo)
    result = s.stdout.replace('\r', '')

    update_count = len(result.splitlines())

    if update_count:
        filename = os.path.join(config.data_dir, '%s.txt' % env.host)
        with open(filename, 'w') as outfile:
            outfile.write(result)

    return update_count

def clear_datadir():
    '''Delete all .txt-files from the data directory.'''
    for f in glob.glob(os.path.join(config.data_dir, '*.txt')):
        os.remove(f)

def collect_update_data(serverlist):
    '''Execute update checks on all hosts in the global server list.

    An email summarizing the pending updates is sent if mailing is
    enabled in the global configuration.

    '''
    clear_datadir()

    metadata_mapping = dict(((s.hostname, s) for s in serverlist))

    with hide('everything'):
        updates = execute(check_for_update,
                          metadata_mapping,
                          hosts=make_host_list(serverlist))

    statfile = os.path.join(config.data_dir, 'statfile')
    open(statfile, 'w').close()

    if config.mail_active:
        update_list = ['%s: %d pending updates' %
                       (host, updates[host]) for host in updates]

        mailtext = update_mail_text.format(
            count=len(updates),
            update_list='\n'.join(update_list),
            updian_uri=config.updian_uri)

        mail = email.mime.text.MIMEText(mailtext)
        mail['Subject'] = update_mail_subject.format(count=len(updates))
        mail['From'] = 'updian <%s>' % (config.mail_from)
        mail['To'] = config.mail_to

        smtp_server = smtplib.SMTP('localhost')
        smtp_server.sendmail(config.mail_from, [config.mail_to],
                             mail.as_string())
        smtp_server.quit()

        print('Mail sent to', config.mail_to)

if __name__ == '__main__':
    from ..serverlist import ServerList

    serverlist = ServerList.from_file(config.serverlist_file)

    collect_update_data(serverlist)

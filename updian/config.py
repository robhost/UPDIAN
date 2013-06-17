# config.py - global configuration
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
'''Updian configuration initialization and config file parsing'''

from ConfigParser import RawConfigParser

# configuration defaults
option_defaults = dict(
    serverlist_file = 'server.json',
    data_dir = 'data',
    todo_dir = 'todo',
    log_dir = 'log',
    updian_uri = 'http://192.168.0.254/updian',
    mail_active = True,
    mail_to = 'root@localhost',
    mail_from = 'updian@localhost',
    concurrency = 20,
    autodetect_backend = True,
    allow_unauthenticated_packages = False,
    secret_key = 'SECRET')

main_section = 'UPDIAN'

example_config = (
'''[%s]
# file containing the server list
serverlist_file = server.json

# secret key used for CSRF and cookie encryption
secret_key = {secret_key}

# url to your installation (used for hyperlinking in mails)
updian_url = http://192.168.0.254/updian/

# send infomails: true|false
mail_active = true
# recipient of infomails, should be your valid email
mail_to     = server@domain.tld
# sender of informails, defaults to updian@localhost, have a look at "hostname -f"
mail_from   = updian@domain.tld

# concurrency options (how man processes to for for update command)
concurrency = 20

# backend auto-detection
# if this is set to false, the default backend (apt) will be used for hosts w/o an explicit backend configuration
autodetect_backend = true

# allow unauthenticated packages
allow_unauthenticated_packages = false
''' % (main_section))

def write_example_config(filename='config.ini'):
    '''Write a configuration example to a file.'''
    from random import choice
    from string import ascii_letters, digits

    secret_len = 32
    secret = ''.join([choice(ascii_letters + digits) for _ in
                      range(secret_len)])

    with open(filename, 'w') as fp:
        fp.write(example_config.format(secret_key = secret))

def read_config_ini(filename='config.ini'):
    '''Read config file and update global configuration variables.'''
    cp = RawConfigParser()

    found = cp.read(filename)

    if len(found) == 0:
        # TODO no config files loaded, using defaults only
        pass

    def get_option(option):
        default = option_defaults[option]

        if not cp.has_option(main_section, option):
            return default

        if isinstance(default, bool):
            return cp.getboolean(main_section, option)
        elif isinstance(default, int):
            return cp.getint(main_section, option)
        elif isinstance(default, float):
            return cp.getfloat(main_section, option)

        return cp.get(main_section, option)

    module_vars = globals()

    for option in option_defaults:
        v = get_option(option)
        module_vars[option] = v

# initialize on import
read_config_ini()

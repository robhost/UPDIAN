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

import types

# configuration defaults
serverlist_file = 'server.json'
data_dir = 'data'
todo_dir = 'todo'
log_dir = 'log'
keep_cfgs = True
updian_uri = 'http://192.168.0.254/updian'
mail_active = True
mail_to = 'root@localhost'
mail_from = 'updian@localhost'
concurrency = 20
autodetect_backend = True
allow_unauthenticated_packages = False

_TRANSLATION_TABLE = {
    '$cfg_file': 'serverlist_file',
    '$log_path': 'log_dir',
}

def update(option_dict):
    '''Update global configuration from the option_dict dictionary.

    The dictionary may include keys read from the config.php file
    (starting with '$'). Those legacy keys will be automatically
    converted to the appropriate option name.
    Quotes and double quotes are automatically stripped from options
    of type string.

    '''
    if not option_dict:
        return

    module_vars = globals()

    # lots of legacy cruft here
    for option, value in option_dict.iteritems():
        # we don't need log_path_rel b/c it's redundant
        if option == '$log_path_rel':
            continue

        try:
            option = _TRANSLATION_TABLE[option]
        except:
            if option.startswith('$'):
                option = option[1:]

        # raise an error if we try to set an unknown option
        if option not in module_vars:
            raise NameError('Unknown configuration option "%s".' % option)

        # convert booleans
        if (type(module_vars[option]) is types.BooleanType and
            type(value) is types.StringType):
            if value.lower() == 'true':
                value = True
            else:
                value = False
        elif (type(module_vars[option]) is types.IntType and
              type(value) is types.StringType):
            value = int(value)
        elif type(module_vars[option]) is types.StringType and (
                value.startswith("'") or value.startswith('"')):
            value = value.strip('\'"') # strip php string delimiters

        # check for type compatibility
        if type(module_vars[option]) != type(value):
            raise TypeError('Option "%s" must be of type %s.' %
                            (option, type(module_vars[option]).__name__))

        module_vars[option] = value

def read_config_php(config_php='config.php'):
    '''Read updian's config.php file and set configuration variables.

    Parsing is only implemented rudimentary. The parser looks for lines
    starting with '$' and splits the line at the assignment-operator
    (=).

    Keyword arguments:
    config_php -- file object or path string of updian's config file

    '''
    def read_config(fp):
        cfg = {}
        for l in (l.split(';', 1)[0] for l in fp.readlines() if
                  l.startswith('$')):
            k, v = l.split('=', 1)
            cfg[k.strip()] = v.strip()

        return cfg

    if isinstance(config_php, file):
        update(read_config(config_php))
    elif isinstance(config_php, str):
        with open(config_php, 'r') as fp:
            update(read_config(fp))
    else:
        raise TypeError('config_php must be a file or string (containing a '
                        'file path).')

# initialize on import
read_config_php()

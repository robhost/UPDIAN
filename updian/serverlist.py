# serverlist.py - serverlist handling
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
'''Updian server list handling'''

from __future__ import print_function

import functools
import json
import operator
import os.path
import sys
import types

FMT_CSV = 'format_csv'
FMT_JSON = 'format_json'

available_formats = [FMT_CSV, FMT_JSON]

class ServerList(list):
    '''Class providing a list interface for updian's server list.

    It also provides convenience methods for loading and dumping the
    list from/to the filesystem.

    '''
    @classmethod
    def from_file(cls, server_file, fmt=available_formats[-1]):
        return read_from_file(server_file, fmt)

    def dump(self, server_file, indent=None):
        def dump_it(slist, fp, indent):
            json.dump(slist, fp, cls=ServerListJSONEncoder, indent=indent)

        if isinstance(server_file, file):
            return dump_it(self, server_file, indent)

        with open(server_file, 'w') as fp:
            return dump_it(self, fp, indent)

    def sort(self):
        super(ServerList, self).sort(key=operator.attrgetter('hostname'))

class ServerListJSONEncoder(json.JSONEncoder):
    '''JSON encoder for Server objects.'''
    def default(self, obj):
        if isinstance(obj, Server):
            return dict(obj)
        return json.JSONEncoder.default(self, obj)

class Server(object):
    defaults = {
        'user': 'root',
        'port': 22,
        'backend': 'apt',
        'gateway': None,
    }

    def __init__(self, hostname, port=None, backend=None, user=None,
                 gateway=None):
        if port and type(port) != types.IntType:
            port = int(port)

        self.hostname = hostname
        self.port = port
        self.backend = backend
        self.user = user
        self.gateway = gateway

    def __iter__(self):
        for attr in self.__dict__:
            if not attr.startswith('_') and getattr(self, attr):
                yield (attr, getattr(self, attr))

    def __repr__(self):
        return repr(dict(self))

    def __eq__(self, other):
        return self.hostname == other.hostname

    def __ne__(self, other):
        return self.hostname != other.hostname

def _file_format_dispatch(function):
    def get_target_function(fmt):
        if fmt not in available_formats:
            raise ValueError("Config file format '%s' not supported." % fmt)

        target_name = '_%s_%s' % (function.__name__, fmt)

        try:
            target_function = globals()[target_name]
        except KeyError:
            raise NotImplementedError("Oops, we forgot to implement '%s' for "
                "format '%s'. Please file a bug report." %
                (function.__name__, fmt))

        if type(target_function) != types.FunctionType:
            raise TypeError("Found '%s' but it's not a function." % target_name)

        return target_function

    if function.__name__.startswith('read_from_'):
        @functools.wraps(function)
        def wrapper(server_file, fmt=available_formats[-1], *args, **kwargs):
            target_function = get_target_function(fmt)

            if isinstance(server_file, file):
                return target_function(server_file, *args, **kwargs)

            with open(server_file, 'r') as fp:
                return target_function(fp, *args, **kwargs)

        return wrapper
    else:
        raise ValueError('file_format_dispatch() only works for '
            'read_from-functions.')

@_file_format_dispatch
def read_from_file():
    '''Read server list from file.'''
    pass

def _read_from_file_format_csv(fp):
    slist = ServerList()

    for line in fp.readlines():
        fields = line.strip().split(':')
        slist.append(Server(*fields))

    return slist

def _read_from_file_format_json(fp):
    def list_entry_hook(dct):
        return Server(**dct)

    deserialized_data = json.load(fp, object_hook=list_entry_hook)

    if not isinstance(deserialized_data, list):
        raise ValueError('Deserialized object was no list.')

    return ServerList(deserialized_data)

def convert_from_csv(old_server_file='server.txt', new_server_file='server.json'):
    if not os.path.exists(old_server_file):
        print('ERROR: %s not found' % old_server_file, file=sys.stderr)

    slist = read_from_file(old_server_file, FMT_CSV)

    if os.path.exists(new_server_file):
        prompt = ('Output file "%s" already exists. Overwrite? [Y/n] '
                  % new_server_file)
        answer = raw_input(prompt).lower()

        if answer in ['n', 'no']:
            new_server_file += '.new'

    slist.dump(new_server_file, 2)

    print('Converted %s to %s.' % (old_server_file, new_server_file))

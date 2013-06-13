# convert_serverlist.py - command to convert old server lists
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

import os

from updian import config, serverlist

sl = config.serverlist_file
if sl.endswith('.txt'):
    print('Converting...')
    slnew = sl.replace('.txt', '.json')
    if os.path.exists(slnew):
        slnew += '.convnew'
    serverlist.convert_from_csv(sl, slnew)
    print('Saving to file %s.' % slnew)
    print('Now please check the converted file and adjust your config file accordingly')
else:
    print('Server list was apparently already converted to JSON. Aborting.')

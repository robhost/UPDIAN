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

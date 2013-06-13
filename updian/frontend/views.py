# views.py - frontend views
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
import os
import time

import flask

from flask import flash, redirect, render_template, request, url_for

from . import forms
from . import validation
from .utils import *
from ..frontend import app
from .. import config
from ..serverlist import Server, ServerList

@app.route('/')
def home():
    return list_updates()

def list_updates():
    template_data = dict()

    statfile = os.path.join(config.data_dir, 'statfile')

    template_data['lastupdate'] = formatted_mtime(statfile)

    host_list = list()
    for hostname in sorted(hosts_with_updates()):
        with open(get_data_filename(hostname), 'r') as f:
            count = sum(1 for line in f)
        host = dict(name=hostname,
                    update_count=count,
                    queued=is_queued(hostname))
        host_list.append(host)

    if host_list:
        template_data['updatelist'] = host_list

    server = request.args.get('server', None)
    if server:
        update_details = get_update_details(server)
        if update_details:
            template_data['update_details'] = update_details

    return render_template('index.html', **template_data)

@app.route('/queue/')
@app.route('/queue/list/')
def show_queue():
    template_data = dict()

    statfile = os.path.join(config.data_dir, 'statfile_upd')

    template_data['lastrun'] = formatted_mtime(statfile)

    host_list = list()
    for hostname in sorted(queued_hosts()):
        mtime = formatted_mtime(get_todo_filename(hostname))
        host = dict(name=hostname,
                    queue_date=mtime)
        host_list.append(host)

    if host_list:
        template_data['updatequeue'] = host_list

    return render_template('queue_show.html', **template_data)

@app.route('/queue/all')
def queue_all_hosts():
    for host in hosts_with_updates():
        queue_host(host)

    return redirect(url_for('home'))

@app.route('/queue/add/<hostname>')
def queue_host(hostname):
    todo_file = get_todo_filename(hostname)
    if not os.path.exists(todo_file):
        open(todo_file, 'w').close()

    return redirect(url_for('home'))

@app.route('/queue/remove/<hostname>')
def dequeue_host(hostname):
    # TODO restrict to POST to get CSRF protection
    todo_file = get_todo_filename(hostname)
    if os.path.exists(todo_file):
        os.remove(todo_file)

    return redirect(url_for('show_queue'))

@app.route('/servers/')
@app.route('/servers/list/')
def list_servers():
    serverlist_file = config.serverlist_file
    if not serverlist_file.endswith('.json'):
        flash('Please convert your server.txt to server.json.')

    try:
        serverlist = get_serverlist(serverlist_file)
        serverlist.sort()
    except ValueError as e:
        e = 'There was an error decoding your server list file: %s\n' % e
        e += 'Maybe you forgot to convert it from the old server.txt format?'
        return critical_error(e)
    except IOError:
        flash('There was an error reading the server list file. '
              'Creating empty server list. '
              'It will be saved once you create the first server.')
        serverlist = ServerList()

    template_data = dict(
        serverlist_file=serverlist_file,
        serverlist=serverlist)

    return render_template('server_list.html', **template_data)

@app.route('/servers/edit/',
           defaults={'hostname': None},
           methods=['GET', 'POST'])
@app.route('/servers/edit/<hostname>', methods=['GET', 'POST'])
def edit_server(hostname):
    try:
        serverlist = get_serverlist()
    except IOError:
        serverlist = ServerList()

    if hostname is None:
        server = Server(None)
    else:
        try:
            server_id = serverlist.index(Server(hostname))
            server = serverlist[server_id]
        except ValueError:
            flash('Host not found')
            return redirect(url_for('list_servers'))

    if request.method == 'POST':
        server = forms.server_from_form(request.form)
        errors = validation.validate_server(server)

        if not request.form['host_id'] and server in serverlist:
            # new hostname is already in serverlist
            errors.insert(0, 'Duplicate hostname. '
                          'A host with the name "%s" already exists.' %
                          server.hostname)

        if errors:
            map(flash, errors)
        else:
            if not request.form['host_id']:
                # new entry
                if server in serverlist:
                    flash()
                else:
                    serverlist.append(server)
            else:
                # edit existing entry
                existing_id = serverlist.index(Server(request.form['host_id']))
                serverlist[existing_id] = server

            serverlist.sort()
            serverlist.dump(config.serverlist_file)

            return redirect(url_for('list_servers'))

    return render_template('server_edit.html', host_id=hostname, server=server)

@app.route('/servers/delete', methods=['POST'])
def delete_server():
    serverlist = get_serverlist()

    host_to_remove = request.form['hostname']
    serverlist.remove(Server(host_to_remove))

    serverlist.dump(config.serverlist_file)

    return redirect(url_for('list_servers'))

@app.route('/logs/')
def list_logs():
    template_data = dict()

    statfile = os.path.join(config.data_dir, 'statfile_upd')

    template_data['lastrun'] = formatted_mtime(statfile)

    log_list = list()
    for hostname in sorted(available_logs()):
        mtime = formatted_mtime(get_log_filename(hostname))
        host = dict(name=hostname,
                    update_date=mtime)
        log_list.append(host)

    if log_list:
        template_data['logs'] = log_list

    return render_template('logs_list.html', **template_data)

@app.route('/logs/show/<hostname>')
def show_logfile(hostname):
    if '..' in hostname or hostname.startswith('/'):
        flask.abort(404)

    logfile = get_log_filename(hostname)

    if not os.path.exists(logfile):
        flask.abort(404)

    return flask.send_file(logfile, 'text/plain')

@app.route('/logs/delete/<hostname>')
def delete_logfile(hostname):
    # TODO use POST to get CSRF protection
    logfile = get_log_filename(hostname)
    if not os.path.exists(logfile):
        flask.abort(404)

    os.remove(logfile)

    return redirect(url_for('list_logs'))

@app.route('/logs/delete_all')
def delete_all_logfiles():
    # FIXME: This has the possibility of deleting more than the user has seen
    for hostname in available_logs():
        delete_logfile(hostname)

    return redirect(url_for('list_logs'))

@app.errorhandler(500)
def critical_error(e):
    return render_template('critical_error.html', error=e), 500

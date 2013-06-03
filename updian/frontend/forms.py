from ..serverlist import Server

def server_from_form(form):
    return Server(hostname=form['hostname'],
                  port=form['port'] or None,
                  backend=form['backend'] or None,
                  user=form['user'] or None,
                  gateway=form['gateway'] or None)

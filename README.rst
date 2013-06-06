Updian v0.6 - UpdateDebian
==========================

RobHost GmbH [support@robhost.de], 2007-2013

License: GPLv2+

PLEASE NOTE THAT THIS SOFTWARE COMES WITH ABSOLUTELY NO WARRANTY!


What is it good for?
--------------------

Updian is a minimalistic update-engine for DEBIAN GNU/Linux based machines
(and other flavours like Ubuntu based on APT) and, since v0.4, for machines
with YUM such as CentOS. You can use it to maintain all your machines
remotely over a simple webinterface written in PHP. There are 2 cronjobs,
one checks for updates, another does them. You can choose from the
webinterface which servers to update (it shows up the packages) and read
logs after the updates are done.

Updian does not need any databases, every data is stored by (mostly) empty
flatfiles. It can manage a high number of servers, I've tested/used it with
100+ servers without any problems ...

Actually, Updian only does "apt-get upgrade", not "dist-upgrade". So it's a
good idea to run "apticron" or anything in parallel on the remote machines to
keep informed about upcoming dist-upgrades. Apticron is also good for checking
the correctness of Updian - it mails you the updates every day including
changelog. These you can now install with Updian. If Updian is working
correctly, apticron should mail you the same update-infos (except
dist-upgrades) as Updian shows up in the webfrontend.

For every server Updian creates an logfile, so you're always informed about
updates made. The logfiles are available through the webfrontend.


Requirements
------------

- Debian GNU/Linux or other apt-running systems (Ubuntu, Knoppix ...) or
  yum-running systems (CentOS, RHEL, Fedora Core ...) on the remote-side
- Any Linux-Distribution on the machine which runs Updian (local-side)
- Python 2.6 or newer (local-side)
- A crond running (local-side)
- Access as root to all involved machines (gaining root via sudo is also
  supported)
- Exchanged SSH-publickeys between the local machine running Updian and the
  remote servers
    - that means you can login from the machine running Updian to the remote
      server via "ssh <server>" without entering a password
    - Howto: On the machine running Updian:
        - ``ssh-keygen -t rsa``
        - ``cat ~/.ssh/id_dsa.pub |
          ssh root@remote_server cat - ">>" ~/.ssh/authorized_keys``
        - OR use ``ssh-copy-id <server>``
- Optional: Web server with WSGI support or
  a separate WSGI application server (local-side)


Installation
------------

From PyPI or from archive via pip (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. TODO

From archive (manually)
^^^^^^^^^^^^^^^^^^^^^^^

- Unzip the files to a folder on your server (the machine where Updian should
  run).
- Edit the config.php according to the instructions inside the file.
- Make sure the data, log and todo directories are writeable by the user
  that will be running updian.
- Install Updian's dependencies Fabric, Flask, flask-csrf and flask-basicauth
  (e.g. via pip: ``pip install Fabric>=1.6.0 Flask>=0.9 flask-csrf>=0.9.2
  flask-basicauth>=0.1.1``).
  Note: It is recommended to use a virtual environment for production usage (see
  `virtualenv documentation`_).
- Optional: Use ``updiancmd setpw`` to create one or more users for basic
  authentication. If you skip this everyone on the network you serve Updian on
  will be able to access it without restriction.
- Run ``updiancmd runserver <local ip address>``.
- Open http://yourhost:5000/ in your web browser.
- Click on "Servers" and add your servers.
- For test purposes run ``updiancmd collect`` on your shell.
    - You should see some output and (if there are updates) the updates should
      be visible via the web interface.
- Run ``updiancmd update`` if you want Updian to update your chosen servers.
- Add cronjobs for full automatic updates (``crontab -e``). Example crontab
  entries::

    0 8 * * * /var/www/updian/updiancmd collect > /dev/null 2>&1 # (collect updates daily at 8 am)
    0 9 * * * /var/www/updian/updiancmd update > /dev/null 2>&1 # (run updates daily at 9 am)

.. _virtualenv documentation: http://www.virtualenv.org/en/latest/


Example configuration using Apache HTTPd 2.x with mod\_wsgi
-----------------------------------------------------------

To use mod\_wsgi on the Apache2 web server you can use something along the
following lines in your virtual host configuration::

    <IfModule mod_wsgi.c>
        WSGIScriptAlias /updian /var/www/updian/updian.wsgi
        WSGIPassAuthorization On

        WSGIDaemonProcess updian-webif python-path=/var/www/updian home=/var/www/updian
        WSGIProcessGroup updian-webif

        Alias /updian/static /var/www/updian/updian/frontend/static

        <Directory /var/www/updian/updian/frontend/static>
            Order allow,deny
            Allow from all
        </Directory>
    </IfModule>

If you have installed Updian's dependencies into a virtual environment you
should add its site-packages directory to the python-path of the daemon
process::

    WSGIDaemonProcess updian-webif python-path=/yourvenv/lib/python2.6/site-packages:/var/www/updian home=/var/www/updian

You can also use ``WSGIPythonHome`` to set an alternative Python interpreter for
mod\_wsgi to use globally (see: `WSGIPythonHome documentation`_).

.. _WSGIPythonHome documentation: http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIPythonHome


Updating from old server.txt format (used in UPDIAN v0.4 and older)
-------------------------------------------------------------------

- Run ``updiancmd convert_sl``
- Update your config.php to point to the newly created file


Checkrestart for updated services on remote machines
----------------------------------------------------

Since v0.3 Updian can check if there are services running on remote machines
that need to be restartet. That is often needed if libs used by many
programs (libssl i.e.) have been updated on the remote machine. After that
it is i.e. required to restart apache or postfix.

Updian uses the script ``checkrestart`` from the package ``debian-goodies`` for
that. Just apply ``apt-get install debian-goodies`` on the desired remote
machines.

It does, in short, anything like this to find out which procs using
deprecated libs: ``lsof -n | egrep -i "(DEL|inode)"``

Updian writes the output from ``checkrestart`` to <server>\_checkrestart.log
(see "Logs" in webfrontend).


UPDIAN restricted shell - updian-rsh
------------------------------------

Updian's default mode of operation gives the updian server unlimited root access
to all servers.
updian-rsh is a shell script that can be used with ssh's forced command feature
to limit the commands updian can execute over ssh. Then, even if the updian
server is compromised, the intruder can only do one thing with your other
servers: Update them. This means that the multi-ssh feature is also restriced to
the commands allowed by updian-rsh.

To use it, copy updian-rsh to the machines you want to update, for example to
/usr/local/bin.
Prefix the line in /root/.ssh/authorized\_keys with

::

    command="/usr/local/bin/updian-rsh"

so that it looks like this:

::

    command="/usr/local/bin/updian-rsh" ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA8Yf[...]

Now when you try to connect to that server with "ssh root@remote\_server"
you should get the message

::

    Updian Restriced Shell: Interactive shell not allowed

and the connection is closed.

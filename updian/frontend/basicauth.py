import os

import flask.ext.basicauth

from .. import passwd

class BasicAuth(flask.ext.basicauth.BasicAuth):
    def __init__(self, app):
        if os.path.exists(passwd.passwd_file):
            app.config['BASIC_AUTH_FORCE'] = True
        super(BasicAuth, self).__init__(app)

    def check_credentials(self, username, password):
        user = passwd.get_user_from_passwd(username)

        if user is not None:
            return passwd.hashpw(password, user[1]) == user[1]

        return False
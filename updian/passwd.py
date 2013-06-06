from __future__ import print_function

import crypt
import getpass
import os
import random
import string
import sys

SALT_CHARACTERS = string.ascii_letters + string.digits + '/.'
SALT_PREFIX = '$6$'

passwd_file = 'updian.passwd'

def gensalt(length):
    if length < 8 or length > 16:
        raise ValueError('Salt length must be between 8 and 16.')

    salt = ''.join([random.choice(SALT_CHARACTERS) for _ in range(length)])

    return salt

def hashpw(password, salt):
    if not salt.startswith(SALT_PREFIX):
        for c in salt:
            if c not in SALT_CHARACTERS:
                raise ValueError('Salt contains invalid character: %s' % c)
        salt = SALT_PREFIX + salt + '$'

    return crypt.crypt(password, salt)

def line_contains_username(line, username):
    return line.startswith(username + ':$')

def get_user_from_passwd(username):
    with open(passwd_file, 'r') as f:
        for line in f:
            if line_contains_username(line, username):
                return line.strip().rsplit(':', 1)
    return None

def set_user_password(username, password):
    if ':$' in username:
        raise ValueError('Username must not contain ":$".')

    if not os.path.exists(passwd_file):
        open(passwd_file, 'w').close()

    user = get_user_from_passwd(username)
    pwhash = hashpw(password, gensalt(16))

    new_user_line = username + ':' + pwhash + '\n'

    if user is None:
        with open(passwd_file, 'a') as f:
            f.write(new_user_line)
    else:
        with open(passwd_file, 'r') as old_passwd:
            lines = old_passwd.readlines()
        with open(passwd_file, 'w') as f:
            for l in lines:
                if line_contains_username(l, username):
                    l = new_user_line
                f.write(l)

def set_interactively():
    if not os.path.exists(passwd_file):
        open(passwd_file, 'w').close()

    username = raw_input('Username: ')

    user = get_user_from_passwd(username)
    if user is not None:
        current_pw = raw_input('Current password: ')
        if hashpw(current_pw, user[1]) != user[1]:
            print('Current password does not match.')
            sys.exit(1)

    password = getpass.getpass('New password: ')
    password2 = getpass.getpass('Repeat new password: ')

    if password != password2:
        print('Passwords do not match')
        sys.exit(1)

    set_user_password(username, password)

if __name__ == '__main__':
    set_interactively()

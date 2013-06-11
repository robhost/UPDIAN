# setup.py - python distribute install script
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
import sys
from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6) or sys.version_info[0] > 2:
    msg = ("UPDIAN requires Python 2.6 or later but does not work on "
           "any version of Python 3. You are using version %s. Please "
           "install using a supported version." % sys.version)
    sys.stderr.write(msg)
    sys.exit(1)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = read('requirements.txt').splitlines()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: System Administrators',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    ]

setup(
    name = 'UPDIAN',
    version = '0.6',
    license = 'GPLv2+ <http://www.gnu.org/licenses/gpl-2.0.en.html>',
    url = 'http://www.robhost.de/updian/',
    description = "A program for monitoring and executing updates on remote systems",
    long_description = read('README.rst'),
    classifiers = CLASSIFIERS,
    author = "Robert Klikics",
    author_email = "rk@robhost.de",
    maintainer = "Dirk Dankhoff",
    maintainer_email = "dd@robhost.de",
    install_requires = requires,
    packages = find_packages(),
    scripts = ['updiancmd'],
    include_package_data = True,
    zip_safe = False,
    )

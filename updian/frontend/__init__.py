import flask
from flaskext.csrf import csrf
from .basicauth import BasicAuth
from .. import config

app = flask.Flask(__name__)
app.secret_key = config.secret_key

csrf(app)

basic_auth = BasicAuth(app)

from . import views

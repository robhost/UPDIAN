import flask
from flaskext.csrf import csrf
from .basicauth import BasicAuth

app = flask.Flask(__name__)
app.secret_key = 'SECRET' # TODO generate in setup

csrf(app)

basic_auth = BasicAuth(app)

from . import views

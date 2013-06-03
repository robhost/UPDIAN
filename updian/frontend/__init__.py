import flask
from flaskext.csrf import csrf

app = flask.Flask(__name__)
app.secret_key = 'SECRET'

csrf(app)

from . import views

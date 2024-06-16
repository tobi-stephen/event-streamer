import datetime
import threading

from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
jwt = JWTManager(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/idea_events'
mongo = PyMongo(app)
db = mongo.db


def db_setup():
    colls = db.list_collection_names()

    if 'users' not in colls:
        user_coll = db.users
        user_coll.create_index('username')
        user_coll.create_index('email')
        user_coll.create_index('user_id')

    if 'events' not in colls:
        events_coll = db.events
        events_coll.create_index('event_id')

with app.app_context():
    db_setup()

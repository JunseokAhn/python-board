from flask import Flask, request, render_template, abort, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import time
import math

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myweb"
app.secret_key = 'some secret key'
app.config["PERMANENT_SESSSION_LIFETIME"] = timedelta(minutes=30)
mongo = PyMongo(app)

from .common import login_required
from .filter import format_datetime
from . import board
from . import member

app.register_blueprint(board.blueprint)
app.register_blueprint(member.blueprint)

from datetime import datetime
from enum import unique
from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    pw_attempt1 = db.Column(db.Integer)
    pw_attempt2 = db.Column(db.Integer)
    pw_attempt3 = db.Column(db.Integer)
    contacts = db.relationship('Contact', backref='subscriber')
    

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    address = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    state = db.Column(db.String(150), nullable=False)
    datestp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


import os
from pymongo import MongoClient
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps
from bson import json_util
from models import User


db_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/euro2024')
client = MongoClient(db_uri)
db = client.get_default_database()


class SignupForm(FlaskForm):
    nickname = StringField("Nickname", [InputRequired("Please enter your nickname. This will be shown on leaderboard")])
    email = StringField("Email", [InputRequired("Please enter your email address."), Email("Please enter your email address. We will not share this email with anyone.")])
    password = PasswordField('Password', [InputRequired("Please enter a password.")])
    submit = SubmitField("Register")
 
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        
        user = db.users.find_one({"email": self.email.data.lower()})
        if user:
            self.email.errors.append("That email is already taken")
            return False
        elif db.users.find_one({"nickname": self.nickname.data.lower()}):
            self.email.errors.append("That nickname is already taken! Please choose another username")
            return False
        else:
            return True


class LoginForm(FlaskForm):
    email = StringField("Email", [InputRequired("Please enter your email address."), Email("Please enter your email address.")])
    password = PasswordField('Password', [InputRequired("Please enter a password.")])
    submit = SubmitField("Sign In")
 
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        
        user = User.find_by_email(self.email.data.lower())
        if user and user.verify_password(self.password.data):
            session['user_id'] = str(user.user_id)
            session['user_nickname'] = user.nickname
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False


def check_password(pwdhash, password):
    return check_password_hash(pwdhash, password)

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, relationship
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    
class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
class BillGroups (db.Model):
    __tablename__='bill_groups'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    group_name = db.Column(db.String(255), unique=True)
    bill_intermediaries = db.relationship("BillGroupIntermediary")

class BillGroupIntermediary (db.Model):
    __tablename__ = 'group_user_intermediary'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column (db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column (db.Integer, db.ForeignKey('bill_groups.id'))
    user = db.relationship("User")
    bill_groups = db.relationship("BillGroups")


class IndividualBill (db.Model):
    __tablename__ = 'individual_bill'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    bill_id = db.Column (db.Integer, db.ForeignKey('bill_groups.id'))
    bill_item = db.Column(db.String(255))
    item_price = db.Column(db.Numeric(100))



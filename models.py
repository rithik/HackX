from flask import Flask
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000), unique=True)
    password = db.Column(db.String(length=1000))
    hash = db.Column(db.String(length=1000), default="")
    is_hacker = db.Column(db.Boolean, default=False)
    is_mentor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    full_name = db.Column(db.String(length=1000), default="")
    school = db.Column(db.String(length=1000), default="")
    grad_year = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(length=100), default="")
    race = db.Column(db.String(length=100), default="")
    describe = db.Column(db.String(length=200), default="")
    why = db.Column(db.String(length=1800), default="")
    major = db.Column(db.String(length=1000), default="")
    birthday = db.Column(db.String(length=1000), default="")
    mlh_rules = db.Column(db.Boolean, default=False)
    hackathons = db.Column(db.Integer, default=0)
    app_complete = db.Column(db.Boolean, default=False)

    travel = db.Column(db.Boolean, default=False)
    where_from = db.Column(db.String(length=1000), default="")
    travel_method = db.Column(db.String(length=1000), default="")
    miles = db.Column(db.String(length=1000), default="")
    cost = db.Column(db.String(length=1000), default="")

    def __repr__(self):
        return '<User: {}>'.format(self.email)

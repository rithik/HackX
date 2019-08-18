from flask import Flask
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from app import db

class Hacker(db.Model):
    __tablename__ = 'hackers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000), unique=True)
    password = db.Column(db.String(length=1000))
    hash = db.Column(db.String(length=1000), default="")
    
    full_name = db.Column(db.String(length=1000), default="")

    application_id = db.Column(db.Integer, default=-1)
    confirmation_id = db.Column(db.Integer, default=-1)

    is_admin = db.Column(db.Boolean, default=False)

    is_mentor = db.Column(db.Boolean, default=False)
    company_name = db.Column(db.String(length=1000), default="")

    verified = db.Column(db.Boolean, default=False)

    application = db.relationship('Application', backref='hacker',
        lazy=True)

    confirmation = db.relationship('Confirmation', backref='hacker',
        lazy=True)

    emails = db.relationship('Email', backref='hacker',
        lazy=True)

    tickets = db.relationship('Ticket', backref='hacker',
        lazy=True)

    company = db.relationship('Company', backref='hacker',
        lazy=True)

    qr_hash = db.Column(db.String(length=1000), default=str(uuid.uuid1()))
    checked_in = db.Column(db.Boolean, default=False)
    sat_breakfast = db.Column(db.Boolean, default=False)
    sat_lunch = db.Column(db.Boolean, default=False)
    sat_dinner = db.Column(db.Boolean, default=False)
    sun_breakfast = db.Column(db.Boolean, default=False)
    sun_lunch = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Hacker: {}>'.format(self.email)

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000), unique=True)

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
    # add resume
    travel = db.Column(db.Boolean, default=False)
    where_from = db.Column(db.String(length=1000), default="")
    travel_method = db.Column(db.String(length=1000), default="")
    miles = db.Column(db.String(length=1000), default="")
    cost = db.Column(db.String(length=1000), default="")

    accepted = db.Column(db.Boolean, default=False)
    waitlisted = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)

    hackerid = db.Column(db.Integer, db.ForeignKey('hackers.id'),
        nullable=False)

    def __repr__(self):
        return '<Application: {}>'.format(self.email)

class Confirmation(db.Model):
    __tablename__ = 'confirmations'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000), unique=True)

    tshirt = db.Column(db.String(length=1000), default="")
    dietary = db.Column(db.String(length=1000), default="")
    phone = db.Column(db.String(length=100), default="")
    github = db.Column(db.String(length=1000), default="")
    notes = db.Column(db.String(length=10000), default="")
    resume_file_name = db.Column(db.String(length=10000), default="")

    confirmed = db.Column(db.Boolean, default=False)
    declined = db.Column(db.Boolean, default=False)

    hackerid = db.Column(db.Integer, db.ForeignKey('hackers.id'),
        nullable=False)

    def __repr__(self):
        return '<Confirmation: {}>'.format(self.email)

class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000))

    uuid = db.Column(db.String(length=1000), unique=True)
    subject = db.Column(db.String(length=1000))
    message = db.Column(db.String(length=20000))
    action = db.Column(db.String(length=1000))
    redirect_url = db.Column(db.String(length=1000))

    sent = db.Column(db.DateTime)
    viewed = db.Column(db.DateTime)

    hackerid = db.Column(db.Integer, db.ForeignKey('hackers.id'),
        nullable=False)

    def __repr__(self):
        return '<Confirmation: {}>'.format(self.email)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=1000))

    question = db.Column(db.String(length=10000))
    location = db.Column(db.String(length=10000))
    contact = db.Column(db.String(length=10000))

    status = db.Column(db.String(length=1000))

    hackerid = db.Column(db.Integer, db.ForeignKey('hackers.id'),
        nullable=False)

    mentorid = db.Column(db.Integer)

    def __repr__(self):
        return '<Ticket: {}>'.format(self.question)

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=1000), default="")

    mentors = db.Column(db.Integer, db.ForeignKey('hackers.id'),
        nullable=False)

    def __repr__(self):
        return '<Ticket: {}>'.format(self.question)

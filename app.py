from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import random
import sys
from database import db_session
import json
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime
from flask_admin import Admin
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView as MV
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import uuid

app = Flask(__name__)

try:
    try:
        if os.environ['FLASK_ENV'] == "development":
            import settings
            app.config['APP_SETTINGS'] = settings.APP_SETTINGS
            app.secret_key = settings.SECRET_KEY
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
            app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
            app.config['BASIC_AUTH_USERNAME'] = settings.ADMIN_USERNAME
            app.config['BASIC_AUTH_PASSWORD'] = settings.ADMIN_PASSWORD
    except:
        app.config['APP_SETTINGS'] = os.environ['APP_SETTINGS']
        app.secret_key = os.environ['SECRET_KEY']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ['SQLALCHEMY_TRACK_MODIFICATIONS']
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        app.config['BASIC_AUTH_USERNAME'] = os.environ['ADMIN_USERNAME']
        app.config['BASIC_AUTH_PASSWORD'] = os.environ['ADMIN_PASSWORD']
except:
    import settings
    app.config['APP_SETTINGS'] = settings.APP_SETTINGS
    app.secret_key = settings.SECRET_KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['BASIC_AUTH_USERNAME'] = settings.ADMIN_USERNAME
    app.config['BASIC_AUTH_PASSWORD'] = settings.ADMIN_PASSWORD

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User

def get_user(request):
    login_hash = request.cookies.get('login_hash')
    u = User.query.filter_by(hash=login_hash)
    if u.count() == 0:
        return False
    return u.first()

@app.route('/logout', methods=["GET", "POST"])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('login_hash', expires=0)
    return resp

@app.route('/', methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        user = get_user(request)
        if user:
            return redirect("/dashboard")
        else:
            return render_template("login_page.html", message="None")
    else:
        if request.form.get('button-type') == "register":
            u = User()
            u.email = request.form['email']
            u.password = generate_password_hash(request.form['password'])
            db.session.add(u)
            db.session.commit()
            return render_template("login_page.html", message="User created!")
        elif request.form.get('button-type') == "login":
            u = User.query.filter_by(email=request.form['email'])
            if u.count() == 0:
                return render_template("login_page.html", message="No account found with this email address!")
            u = u.first()
            if check_password_hash(u.password, request.form['password']):
                resp = make_response(redirect("/dashboard"))
                u.hash = uuid.uuid1()
                db.session.add(u)
                db.session.commit()
                resp.set_cookie('login_hash', u.hash)
                return resp
            else:
                return render_template("login_page.html", message="Incorrect Password!")

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    u = get_user(request)
    if not u:
        return redirect("/")
    return render_template("dashboard.html", user=u,
        submission_deadline=settings.APPLICATION_SUBMISSION_DEADLINE.strftime("%B %d, %Y %I:%M:%S %Z"))

@app.route('/application', methods=["GET", "POST"])
def application():
    u = get_user(request)
    if not u:
        return redirect("/")
    if not request.method == "POST":
        return render_template("application.html", user=u,
            schools=settings.SCHOOLS, genders=settings.GENDERS,
            races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
            travel_methods=settings.TRAVEL_METHODS, msg="")
    if request.method == "POST":
        button_type = request.form.get('button-type', '')
        if button_type == "travel":
            travel = request.form.get('travel', '')
            where_from = request.form.get('where-from', '')
            travel_method = request.form.get('travel-method', '')
            miles = request.form.get('miles', '')
            cost = request.form.get('cost', '')
            if travel == "on":
                u.travel = True
                u.where_from = where_from
                u.travel_method = travel_method
                u.miles = miles
                u.cost = cost
            else:
                u.travel = False
            db.session.add(u)
            db.session.commit()
            return render_template("application.html", user=u,
                schools=settings.SCHOOLS, genders=settings.GENDERS,
                races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
                travel_methods=settings.TRAVEL_METHODS,
                msg="Your travel application has been submitted!")
        full_name = request.form.get('full-name', '')
        birthday = request.form.get('birthday', '')
        school = request.form.get('school', '')
        grad_year = request.form.get('grad-year', '')
        gender = request.form.get('gender', '')
        race = request.form.get('race', '')
        describe = request.form.get('describe', '')
        major = request.form.get('major', '')
        hackathons = request.form.get('hackathons', '')
        why = request.form.get('why', '')
        mlh = request.form.get('mlh', '')
        u.full_name = full_name
        u.birthday = birthday
        u.school = school
        u.grad_year = grad_year
        u.gender = gender
        u.race = race
        u.describe = describe
        u.major = major
        u.hackathons = hackathons
        u.why = why
        if mlh == "on":
            u.mlh_rules = True
        else:
            u.mlh_rules = False
        u.app_complete = True
        db.session.add(u)
        db.session.commit()
        return render_template("application.html", user=u,
            schools=settings.SCHOOLS, genders=settings.GENDERS,
            races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
            travel_methods=settings.TRAVEL_METHODS,
            msg="Your application has been submitted!")

if __name__ == '__main__':
    app.run()

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

from models import Hacker, Application, Confirmation

def get_hacker(request):
    login_hash = request.cookies.get('login_hash')
    u = Hacker.query.filter_by(hash=login_hash)
    if u.count() == 0:
        return False
    return u.first()

def get_application(request):
    login_hash = request.cookies.get('login_hash')
    u = Hacker.query.filter_by(hash=login_hash)
    if u.count() == 0:
        return False
    user = u.first()
    email = user.email
    a = Application.query.filter_by(email=email)
    if u.count() == 0:
        return False
    return a.first()

def get_confirmation(request):
    login_hash = request.cookies.get('login_hash')
    u = Hacker.query.filter_by(hash=login_hash)
    if u.count() == 0:
        return False
    user = u.first()
    email = user.email
    c = Confirmation.query.filter_by(email=email)
    if u.count() == 0:
        return False
    return c.first()

@app.route('/logout', methods=["GET", "POST"])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('login_hash', expires=0)
    return resp

@app.route('/', methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        user = get_hacker(request)
        if user:
            return redirect("/dashboard")
        else:
            return render_template("login_page.html", message="None")
    else:
        if request.form.get('button-type') == "register":
            email = request.form['email']
            f = Hacker.query.filter_by(email=email)
            if not f.count() == 0:
                return render_template("login_page.html", message="There is already an account found with this email address!")
            a = Application()
            a.email = email
            c = Confirmation()
            c.email = email
            db.session.add(a)
            db.session.add(c)
            u = Hacker()
            u.email = email
            u.password = generate_password_hash(request.form['password'])
            u.is_hacker = True
            u.application_id = a.id
            u.confirmation_id = c.id
            db.session.add(u)
            db.session.commit()
            return render_template("login_page.html", message="Hacker account created!")
        elif request.form.get('button-type') == "login":
            u = Hacker.query.filter_by(email=request.form['email'])
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
    u = get_hacker(request)
    a = get_application(request)
    if not u or not a:
        return redirect("/logout")
    return render_template("dashboard.html", user=u, app=a,
        highlight="dashboard",
        submission_deadline=settings.APPLICATION_SUBMISSION_DEADLINE_FMT)

@app.route('/application', methods=["GET", "POST"])
def application():
    u = get_hacker(request)
    a = get_application(request)
    if not u:
        return redirect("/logout")
    if not request.method == "POST":
        return render_template("application.html", user=u, app=a,
            schools=settings.SCHOOLS, genders=settings.GENDERS,
            races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
            highlight="application",
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
                a.travel = True
                a.where_from = where_from
                a.travel_method = travel_method
                a.miles = miles
                a.cost = cost
            else:
                a.travel = False
            db.session.add(a)
            db.session.commit()
            return render_template("application.html", user=u,app=a,
                schools=settings.SCHOOLS, genders=settings.GENDERS,
                races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
                travel_methods=settings.TRAVEL_METHODS,
                highlight="application",
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
        a.full_name = full_name
        a.birthday = birthday
        a.school = school
        a.grad_year = grad_year
        a.gender = gender
        a.race = race
        a.describe = describe
        a.major = major
        a.hackathons = hackathons
        a.why = why
        if mlh == "on":
            a.mlh_rules = True
        else:
            a.mlh_rules = False
        a.app_complete = True
        db.session.add(a)
        db.session.commit()
        return render_template("application.html", user=u, app=a,
            schools=settings.SCHOOLS, genders=settings.GENDERS,
            races=settings.RACES, grad_year=settings.GRADUATION_YEARS,
            travel_methods=settings.TRAVEL_METHODS,
            highlight="application",
            msg="Your application has been submitted!")

@app.route('/admin', methods=["GET", "POST"])
def admin_main():
    u = get_hacker(request)
    if not u:
        return redirect("/logout")
    return render_template("admin.html", highlight="admin", user=u)

@app.route('/admin/users', methods=["GET", "POST"])
def admin_users():
    u = get_hacker(request)
    if not u:
        return redirect("/logout")
    return render_template("admin-users.html", highlight="admin", all_applications=Application.query.all())

@app.context_processor
def event_name():
    return dict(event_name=settings.EVENT_NAME)

@app.route('/create_users', methods=["GET", "POST"])
def create_hackers():
    for k in range(10, 100):
        a = Application()
        a.email = "email" + str(k) + "@gmail.com"
        c = Confirmation()
        c.email = "email" + str(k) + "@gmail.com"
        db.session.add(a)
        db.session.add(c)
        u = Hacker()
        u.email = "email" + str(k) + "@gmail.com"
        u.password = generate_password_hash("q")
        u.is_hacker = True
        u.application_id = a.id
        u.confirmation_id = c.id
        db.session.add(u)
        a.full_name = "User " + str(k)
        a.birthday = "2000-04-19"
        a.school = random.choice(settings.SCHOOLS)
        a.grad_year = random.choice(settings.GRADUATION_YEARS)
        a.gender = random.choice(settings.GENDERS)
        a.race = random.choice(settings.RACES)
        a.describe = "Hacker"
        a.major = "Computer Science"
        a.hackathons = random.randint(0, 10)
        a.why = "Test Message"
        a.mlh_rules = True
        a.app_complete = True
        db.session.add(a)
    db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run()

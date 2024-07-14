from flask import Blueprint, redirect, url_for, flash, session, request, render_template
from flask_login import login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from models import User, db
from config import Config
from forms import SetPasswordForm, LoginForm, RegistrationForm, OTPLoginForm
from utils import send_otp, verify_otp
import random
import string

auth = Blueprint('auth', __name__)

client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.has_set_password and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)
@auth.route('/login/otp', methods=['GET', 'POST'])
def login_otp():
    form = OTPLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            user = User(email=form.email.data, first_name='', last_name='')
            db.session.add(user)
            db.session.commit()
        
        otp = ''.join(random.choices(string.digits, k=6))
        send_otp(user.email, otp)
        session['otp'] = otp
        session['user_id'] = user.user_id
        return redirect(url_for('auth.verify_otp_route'))
    return render_template('login_otp.html', form=form)

@auth.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp_route():
    if 'otp' not in session or 'user_id' not in session:
        return redirect(url_for('auth.login_otp'))
    
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if verify_otp(session['otp'], user_otp):
            user = User.query.get(session['user_id'])
            login_user(user)
            session.pop('otp', None)
            session.pop('user_id', None)
            if not user.has_set_password:
                return redirect(url_for('auth.set_password'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid OTP', 'error')
    return render_template('verify_otp.html')



@auth.route('/login/google')
def login_google():
    google_provider_cfg = requests.get('https://accounts.google.com/.well-known/openid-configuration').json()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('auth.callback', _external=True),
        scope=['openid', 'email', 'profile'],
    )
    return redirect(request_uri)

@auth.route('/login/callback')
def callback():
    code = request.args.get('code')
    google_provider_cfg = requests.get('https://accounts.google.com/.well-known/openid-configuration').json()
    token_endpoint = google_provider_cfg['token_endpoint']
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for('auth.callback', _external=True),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
    )
    
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get('email_verified'):
        unique_id = userinfo_response.json()['sub']
        users_email = userinfo_response.json()['email']
        users_name = userinfo_response.json()['given_name']
    else:
        return 'User email not available or not verified by Google.', 400
    
    user = User.query.filter_by(email=users_email).first()
    if not user:
        names = users_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''
        user = User(email=users_email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()

    login_user(user)

    if not user.has_set_password:
        flash('Please set a password for your account.', 'info')
        return redirect(url_for('auth.set_password'))
    
    return redirect(url_for('main.dashboard'))

@auth.route('/set_password', methods=['GET', 'POST'])
@login_required
def set_password():
    if current_user.has_set_password:
        return redirect(url_for('main.dashboard'))
    
    form = SetPasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been set successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('set_password.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            l=len(form.email.data)
            first_name=form.email.data.split('@')[0][0:l//2]
            last_name=form.email.data.split('@')[0][l//2:l]
            user = User(email=form.email.data, first_name=first_name, last_name=last_name)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('registration.html', form=form)
@auth.route('/register/otp', methods=['GET', 'POST'])
def register_otp():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            user = User.query.filter_by(email=email).first()
            if not user:
                otp = ''.join(random.choices(string.digits, k=6))
                send_otp(email, otp)
                session['register_otp'] = otp
                session['register_email'] = email
                return redirect(url_for('auth.verify_register_otp'))
            else:
                flash('Email already registered', 'error')
    return render_template('register_otp.html')

@auth.route('/register/verify-otp', methods=['GET', 'POST'])
def verify_register_otp():
    if 'register_otp' not in session or 'register_email' not in session:
        return redirect(url_for('auth.register_otp'))
    
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if verify_otp(session['register_otp'], user_otp):
            email = session['register_email']
            user = User(email=email, first_name='', last_name='')
            db.session.add(user)
            db.session.commit()
            login_user(user)
            session.pop('register_otp', None)
            session.pop('register_email', None)
            flash('Registration successful. Please set your password.', 'success')
            return redirect(url_for('auth.set_password'))
        else:
            flash('Invalid OTP', 'error')
    return render_template('verify_register_otp.html')

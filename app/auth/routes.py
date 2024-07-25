from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app , session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.forms import SetPasswordForm , OTPLoginForm , OTPVerify
from utils import send_otp , otp_verification
import requests
import json
import random , string

auth = Blueprint('auth', __name__)

default_role = 'user'

#General Login and signup using username and password 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            
            if user.is_librarian():
                return redirect(url_for('librarian.dashboard'))
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user:
            flash('Username already exists')
        
        else:
            new_user = User(username=username, email=email, role = default_role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('main.home'))
        
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

#Google Login Routes 
@auth.route('/login/google')
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = current_app.config['GOOGLE_PROVIDER_CFG']
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    client = current_app.extensions['oauth_client']
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri= url_for('auth.google_callback' , _external = True),
        scope=["openid", "email", "profile"],
        prompt="select_account",  # This forces the account selection
    )
    return redirect(request_uri)

@auth.route('/login/google/callback')
def google_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = current_app.config['GOOGLE_PROVIDER_CFG']
    token_endpoint = google_provider_cfg["token_endpoint"]

    client = current_app.extensions['oauth_client']
    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(
            username=users_name, email=users_email, role='user', has_set_password=False
        )
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user to password setup page if they haven't set a password yet
    if not user.has_set_password:
        return redirect(url_for('auth.set_password'))

    # Send user back to homepage
    return redirect(url_for('main.home'))


@auth.route('/login/otp', methods = ['GET' , 'POST'])
def otp_login():
    form = OTPLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if not user:
            user = User(
                username = form.username.data , email = form.email.data ,role = 'user' , has_set_password=False
            )

            db.session.add(user)
            db.session.commit()

        otp = ''.join(random.choices(string.digits, k=6))
        send_otp(user.email , otp)
        session['otp'] = otp
        session['user_id'] = user.get_id()

        return redirect(url_for('auth.verify_otp'))
    
    return render_template('otp_login.html' , form=form)

@auth.route('/login/verify_otp', methods = ['Get' , 'POST'])
def verify_otp():

    form = OTPVerify()
    if 'otp' not in session and 'user_id' not in session:
        return url_for('auth.otp_login')
    
    if form.validate_on_submit():
        
        print("user id in session not found :: " , session['user_id'])

        if(otp_verification(session['otp'] , form.otp.data)):
            user = User.query.filter_by(id = session['user_id']).first()

            if not user:
                 return 'null'

            login_user(user)

            session.pop('otp', None)
            session.pop('user_id', None)

            if not user.has_set_password:
                return redirect(url_for('auth.set_password'))
            
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Invalid OTP', 'error')
    
    return render_template('verify_otp.html' , form = form)

@auth.route('/set_password', methods=['GET', 'POST'])
@login_required
def set_password():
    if current_user.has_set_password:
        return redirect(url_for('main.home'))

    form = SetPasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been set successfully.', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('set_password.html', form=form)
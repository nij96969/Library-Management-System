from flask import Blueprint, render_template,redirect,url_for,flash
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.has_set_password:
        flash('Please set a password for your account.', 'info')
        return redirect(url_for('auth.set_password'))
    return render_template('dashboard.html')
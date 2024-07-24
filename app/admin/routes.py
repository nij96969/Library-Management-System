from flask import Blueprint, render_template , redirect , url_for , flash
from flask_login import login_required , current_user
from functools import wraps

admin = Blueprint('admin' , __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin or not current_user.is_authenticated:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/admin/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

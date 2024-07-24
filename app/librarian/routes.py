from flask import Blueprint, render_template , redirect , url_for , flash
from flask_login import login_required , current_user
from functools import wraps

librarian = Blueprint('librarian' , __name__)

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_librarian or not current_user.is_authenticated:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function

@librarian.route('/librarian/dashboard')
@login_required
@librarian_required
def dashboard():
    return render_template('librarian/dashboard.html')

@librarian.route('/librarian/accept_request')
@login_required
@librarian_required
def accept_request():
    return

@librarian.route('/librarian/reject_request')
@login_required
@librarian_required
def reject_request():
    return




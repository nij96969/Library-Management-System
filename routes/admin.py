from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Book, Transaction
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.role = request.form['role']
        db.session.commit()
        flash('User role updated successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/edit_user.html', user=user)

@admin.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        password = request.form['password']

        user = User(email=email, first_name=first_name, last_name=last_name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/create_user.html')

@admin.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/manage_books')
@login_required
@admin_required
def manage_books():
    books = Book.query.all()
    return render_template('admin/manage_books.html', books=books)

@admin.route('/add_book', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    if request.method == 'POST':
        new_book = Book(
            isbn=request.form['isbn'],
            title=request.form['title'],
            author=request.form['author'],
            publisher=request.form['publisher'],
            publishDate=request.form['publishDate'],
            genre=request.form['genre'],
            quantity=int(request.form['quantity']),
            available=int(request.form['quantity'])
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully.', 'success')
        return redirect(url_for('admin.manage_books'))
    return render_template('admin/add_book.html')

@admin.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.isbn = request.form['isbn']
        book.title = request.form['title']
        book.author = request.form['author']
        book.publisher = request.form['publisher']
        book.publishDate = request.form['publishDate']
        book.genre = request.form['genre']
        book.quantity = int(request.form['quantity'])
        book.available = int(request.form['available'])
        db.session.commit()
        flash('Book updated successfully.', 'success')
        return redirect(url_for('admin.manage_books'))
    return render_template('admin/edit_book.html', book=book)

@admin.route('/delete_book/<int:book_id>')
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully.', 'success')
    return redirect(url_for('admin.manage_books'))

@admin.route('/view_transactions')
@login_required
@admin_required
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('admin/view_transactions.html', transactions=transactions)
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Book, Transaction
from functools import wraps

librarian = Blueprint('librarian', __name__)

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_librarian and not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@librarian.route('/dashboard')
@login_required
@librarian_required
def dashboard():
    return render_template('librarian/dashboard.html')

@librarian.route('/manage_books')
@login_required
@librarian_required
def manage_books():
    books = Book.query.all()
    return render_template('librarian/manage_books.html', books=books)

@librarian.route('/add_book', methods=['GET', 'POST'])
@login_required
@librarian_required
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
        return redirect(url_for('librarian.manage_books'))
    return render_template('librarian/add_book.html')

@librarian.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@librarian_required
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
        return redirect(url_for('librarian.manage_books'))
    return render_template('librarian/edit_book.html', book=book)

@librarian.route('/delete_book/<int:book_id>')
@login_required
@librarian_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully.', 'success')
    return redirect(url_for('librarian.manage_books'))

@librarian.route('/view_transactions')
@login_required
@librarian_required
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('librarian/view_transactions.html', transactions=transactions)
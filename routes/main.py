from flask import Blueprint, render_template,redirect,url_for,flash,request
from flask_login import login_required, current_user
from models import Book, db,Transaction
from datetime import datetime

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

@main.route('/user_home')
@login_required
def user_home():
    return render_template('user_home.html')

@main.route('/search_books', methods=['GET', 'POST'])
@login_required
def search_books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        books = Book.query.filter(
            (Book.title.contains(search_query)) |
            (Book.author.contains(search_query)) |
            (Book.isbn.contains(search_query))
        ).all()
        return render_template('search_results.html', books=books, query=search_query)
    return render_template('search_books.html')

@main.route('/book/<int:book_id>')
@login_required
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

@main.route('/borrow_book/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.available > 0:
        # Create a new transaction
        new_transaction = Transaction(user_id=current_user.user_id, book_id=book.book_id)
        book.available -= 1
        db.session.add(new_transaction)
        db.session.commit()
        flash('Book borrowed successfully.', 'success')
    else:
        flash('This book is currently unavailable.', 'error')
    return redirect(url_for('main.book_details', book_id=book_id))

@main.route('/return_book/<int:transaction_id>', methods=['POST'])
@login_required
def return_book(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id == current_user.user_id and not transaction.return_date:
        transaction.return_date = datetime.utcnow()
        transaction.book.available += 1
        db.session.commit()
        flash('Book returned successfully.', 'success')
    else:
        flash('Invalid return request.', 'error')
    return redirect(url_for('main.user_home'))
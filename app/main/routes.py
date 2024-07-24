from flask import Blueprint, render_template , redirect , url_for , request , flash , session
from flask_login import login_required
from app.models import Book , User , RequestBook , BorrowedBook , Transaction
from datetime import datetime, timedelta
from app.models import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/search', methods=['GET', 'POST'])
def search_books():
    search_query = ''
    results = []
    if request.method == 'POST':
        
        search_query = request.form.get('search_query', '').strip()
        
        # Perform the search query based on the title
        results = Book.query.filter(Book.title.ilike(f"%{search_query}%")).all()

    return render_template('home.html', results=results, query=search_query)

@login_required
@main.route('/request_book', methods=['POST'])
def request_book():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')

    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    

    if not user or not book:
        flash('Invalid user or book', 'danger')
        return redirect(url_for('main.home'))

    # Check if the book is already borrowed
    borrowed = BorrowedBook.query.filter_by(book_id=book_id, is_returned=False).first()
    requested_before = RequestBook.query.filter_by(book_id=book_id , user_id=user_id).first()
    if borrowed:
        flash('The book is already borrowed.', 'warning')
    elif requested_before:
        flash('Book has already been requested')
    else:
        # Book is available, so borrow it directly
        request_date = datetime.now()
        
        requested_book = RequestBook(user_id=user_id, book_id=book_id, request_date=request_date)
        db.session.add(requested_book)
        
        # transaction = Transaction(user_id=user_id, book_id=book_id, transaction_type='borrow', time_stamp=borrow_date)
        # db.session.add(transaction)
        
        db.session.commit()
        
        flash('Book Request sent')
    
    return redirect(url_for('main.home'))

@login_required
@main.route('/return_book')
def return_book():
    return

@main.route('/protected')
@login_required
def protected():
    return "This is a protected page. You need to be logged in to see it."
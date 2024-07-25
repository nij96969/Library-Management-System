from flask import Blueprint, render_template , redirect , url_for , request , flash , session
from flask_login import login_required , current_user
from app.models import Book , User , RequestBook , BorrowedBook , ReturnBook
from datetime import datetime
from app.models import db
from sqlalchemy.orm import joinedload

main = Blueprint('main', __name__)

def books_in_library(search_query):
    return Book.query.filter(Book.title.ilike(f"%{search_query}%")).all()

def find_borrowed_book():
    return BorrowedBook.query.options(joinedload(BorrowedBook.book)).filter_by(user_id=current_user.id).all()

@main.route('/')
def home():
    borrowed_books = find_borrowed_book()
    session['borrowed_books'] = [book.to_dict() for book in borrowed_books]
    return render_template('home.html', borrowed_books=session.get('borrowed_books',[]))

@main.route('/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        results = books_in_library(search_query)
        borrowed_books = find_borrowed_book()

        # Store in session
        session['search_query'] = search_query
        session['results'] = [book.to_dict() for book in results]
        session['borrowed_books'] = [book.to_dict() for book in borrowed_books]

    # Retrieve from session
    search_query = session.get('search_query', '')
    results = session.get('results', [])
    borrowed_books = session.get('borrowed_books', [])

    return render_template('home.html', results=results, query=search_query, borrowed_books=borrowed_books)


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
        
        db.session.commit()
        
        flash('Book Request sent')
    
    # Retrieve from session
    search_query = session.get('search_query', '')
    results = session.get('results', [])
    borrowed_books = session.get('borrowed_books', [])

    return render_template('home.html', results=results, query=search_query , borrowed_books=borrowed_books)

@login_required
@main.route('/return_book', methods=['POST'])
def return_book():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')
    
    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if not user or not book:
        flash('Invalid user or book', 'danger')
        return redirect(url_for('main.home'))
    
    return_request = ReturnBook.query.filter_by(user_id=user_id , book_id=book_id).first()

    if return_request:
        flash('Return Request has already been submitted')
    else:
        request_date = datetime.now()
        return_request = ReturnBook(user_id=user_id , book_id=book_id , request_date=request_date)

        db.session.add(return_request)

        db.session.commit()

        flash('Request to return Book sent')

    # Retrieve from session
    search_query = session.get('search_query', '')
    results = session.get('results', [])
    borrowed_books = session.get('borrowed_books', [])

    return render_template('home.html', results=results, query=search_query , borrowed_books=borrowed_books)

@main.route('/refresh', methods = ['POST'])
@login_required
def refresh():
    # Retrieve from session
    search_query = session.get('search_query', '')
    results = session.get('results', [])
    
    borrowed_books = find_borrowed_book()
    session['borrowed_books'] = [book.to_dict() for book in borrowed_books]
    borrowed_books = session.get('borrowed_books',[])


    return render_template('home.html', results=results, query=search_query, borrowed_books=borrowed_books)
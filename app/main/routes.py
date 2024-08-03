from flask import Blueprint, render_template , redirect , url_for , request , flash , session
from flask_login import login_required , current_user
from app.models import Book , User , RequestBook , BorrowedBook , ReturnBook , Transaction
from datetime import datetime
from app.models import db
from sqlalchemy.orm import joinedload
import requests , json
from urllib.parse import unquote

main = Blueprint('main', __name__)

def books_in_library(search_query):
    results = Book.query.filter(Book.title.ilike(f"%{search_query}%")).all()
    return [book.to_dict() for book in results]

def find_borrowed_book():
    borrowed_books = BorrowedBook.query.options(joinedload(BorrowedBook.book)).filter_by(user_id=current_user.id).all()
    return [book.to_dict() for book in borrowed_books]

@main.route('/')
def start_app():
    return redirect(url_for('main.home'))

@main.route('/home')
def home():
        return render_template('home.html')

@main.route('/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        print("Search Query :: " , search_query)
        results=books_in_library(search_query)
        # print(results)
        return render_template('home.html' , results = results , query = search_query)

    return redirect(url_for('main.home'))

@login_required
@main.route('/request_book', methods=['POST'])
def request_book():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')

    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    query = request.form.get('search_query')
    results = request.form.get('results')
    print(query)
    print("Results from UI ::" , results)
    if not user or not book:
        flash('Invalid user or book', 'danger')
        return redirect(url_for('main.home',result=books_in_library(query)))

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
        # Serialize book data
    return redirect(url_for('main.show_book_description',book_id = book_id))

@login_required
@main.route('/return_book', methods=['POST'])
def return_book():
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')
    book_data = request.form.get('book_data')

    print(book_data)
    
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

    return redirect(url_for('main.show_borrowed_books'))

@main.route('/refresh', methods = ['POST'])
@login_required
def refresh():
    return redirect(url_for('main.show_borrowed_books'))

@main.route('/borrowed_books')
@login_required
def show_borrowed_books():
    return render_template('user/borrowed_books.html',borrowed_books = find_borrowed_book())

@main.route('/recommend_books')
@login_required
def show_recommended_books():
    if 'recommendations_generated' not in session:
            # Make a POST request to get recommendations

            #Write the logic for obtaining getting transaction as user history with usr_id & borrow as filter and than use book id to get title of it
            #use the last 5 transaction from the transaction for recommending books 
            
            book_ids = Transaction.query.filter_by(user_id = current_user.id , transaction_type = "borrow").all()

            book_ids = list(dict.fromkeys([book.book_id for book in book_ids][-5:]))

            response = requests.post('http://localhost:8000/recommend', 
                         json={'book_ids': book_ids})

            # Check if the response was successful
            if response.status_code == 200:
                recommendations = response.json().get('recommendations', [])
                # Store the recommendations in the session
                session['recommendations_generated'] = recommendations
            else:
                session['recommendations_generated'] = []

    return render_template('user/recommended_books.html' , recommendations = session.get('recommendations_generated'))

@main.route('/show_description/<int:book_id>', methods=['GET'])
@login_required
def show_book_description(book_id):
        book = Book.query.filter_by(book_id=book_id).first()
        return render_template("user/description.html", book=book.complete_info_to_dict())


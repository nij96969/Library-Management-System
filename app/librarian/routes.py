from flask import Blueprint, render_template , redirect , url_for , flash , request , session
from flask_login import login_required , current_user
from functools import wraps
from app.models import RequestBook , Transaction , BorrowedBook , db , ReturnBook
from datetime import datetime, timedelta

librarian = Blueprint('librarian' , __name__)

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_librarian() or not current_user.is_authenticated:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function

def update_session_requests():
    user_request = RequestBook.query.all()
    user_request = [user_req.to_dict() for user_req in user_request]
    session['user_request_book'] = user_request
    return user_request

def update_session_return_request():
    user_return_book = ReturnBook.query.all()
    user_return_book = [user_req.to_dict() for user_req in user_return_book]
    session['user_return_book'] = user_return_book
    return user_return_book

@librarian.route('/librarian/dashboard')
@login_required
@librarian_required
def dashboard():
    update_session_requests()
    update_session_return_request()
    return render_template('librarian/dashboard.html' , requests = session.get('user_request_book',[]) , returns = session.get('user_return_book',[]))

@librarian.route('/librarian/accept_request', methods = ['POST'])
@login_required
@librarian_required
def accept_request():
    if request.method == 'POST':

        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        if not user_id or not book_id:
            flash('Invalid user or book ID.')
            return redirect(url_for('librarian.dashboard'))

        request_already_accepted = BorrowedBook.query.filter_by(book_id=book_id).first()

        if request_already_accepted:
            flash('request already processed')
            return redirect(url_for('librarian.dashboard'))
        
        # Book is available, so borrow it directly
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)  # Assuming a 2-week borrowing period
        
        borrowed_book = BorrowedBook(user_id=user_id, book_id=book_id, borrow_date=borrow_date, return_date=due_date)
        db.session.add(borrowed_book)
        
        transaction = Transaction(user_id=user_id, book_id=book_id, transaction_type='borrow', time_stamp=borrow_date)
        db.session.add(transaction)
        
        # Find and remove the request from RequestBook
        remove_request = RequestBook.query.filter_by(user_id=user_id, book_id=book_id).first()
        if remove_request:
            db.session.delete(remove_request)
        else:
            flash('Request not found.')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing the request: ' + str(e))
            return render_template('librarian/dashboard.html')

        return redirect(url_for('librarian.dashboard'))
    
    return redirect(url_for('librarian.dashboard'))

@librarian.route('/librarian/reject_request', methods=['POST'])
@login_required
@librarian_required
def reject_request():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        if not user_id or not book_id:
            flash('Invalid user or book ID.')
            return redirect(url_for('librarian.dashboard'))
        
        rejection_date = datetime.now()
        
        remove_request = RequestBook.query.filter_by(user_id=user_id, book_id=book_id).first()

        if remove_request:
            transaction = Transaction(user_id=user_id, book_id=book_id, transaction_type='rejected', time_stamp=rejection_date)
            db.session.add(transaction)
            db.session.delete(remove_request)
        else:
            flash('Request not found.')

        # Update session state
        update_session_requests()
        update_session_return_request()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing the request: ' + str(e))
        
        return redirect(url_for('librarian.dashboard'))
    
    return redirect(url_for('librarian.dashboard'))

@librarian.route('/librarian/accept_return_request', methods=['POST'])
@login_required
@librarian_required
def accept_return_request():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        if not user_id or not book_id:
            flash('Invalid user or book ID.')
            return redirect(url_for('librarian.dashboard'))

        # Check if the book is currently borrowed
        borrowed_book = BorrowedBook.query.filter_by(user_id=user_id, book_id=book_id).first()
        return_request_book = ReturnBook.query.filter_by(user_id=user_id, book_id=book_id).first()
        if not borrowed_book:
            flash('No active borrow record found for this book.')
            return redirect(url_for('librarian.dashboard'))

        # Process return
        return_date = datetime.now()
        
        # Update the borrow record with the return date
        borrowed_book.return_date = return_date
        db.session.commit()

        # Record the return transaction
        transaction = Transaction(user_id=user_id, book_id=book_id, transaction_type='return', time_stamp=return_date)
        db.session.add(transaction)

        db.session.delete(borrowed_book)
        db.session.delete(return_request_book)
        # Remove the return request from the session if necessary
        # update_session_return_request() if you have such a function

        update_session_return_request()
        update_session_requests()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing the return request: ' + str(e))
            return redirect(url_for('librarian.dashboard'))

        # Redirect to dashboard with updated session state
        return redirect(url_for('librarian.dashboard'))
    
    return redirect(url_for('librarian.dashboard'))

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Import db from app instead of creating a new instance
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Changed to plural for consistency

    id = db.Column(db.Integer, primary_key=True)  # user_id
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(8))
    has_set_password = db.Column(db.Boolean, default=False)

    transactions = db.relationship('Transaction', back_populates='user')
    requests = db.relationship('RequestBook', back_populates='user')
    borrowed_books = db.relationship('BorrowedBook', back_populates='user')
    return_books = db.relationship('ReturnBook', back_populates='user') 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.has_set_password = True

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) if self.password_hash else False
    
    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == "admin"
    
    def is_librarian(self):
        return self.role == "librarian"
    
class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(17), nullable=True, server_default="N/A")
    title = db.Column(db.String(255), nullable=False, server_default="N/A")
    authors = db.Column(db.String(255), nullable=False, server_default="N/A")
    published_date = db.Column(db.String(50), nullable=False, server_default="N/A")
    description = db.Column(db.Text, nullable=True, server_default="N/A")
    page_count = db.Column(db.Integer, nullable=True, server_default="0")
    maturity_rating = db.Column(db.String(50), nullable=True, server_default="N/A")
    image_links = db.Column(db.String(255), nullable=True, server_default="N/A")
    language = db.Column(db.String(10), nullable=False, server_default="N/A")
    categories = db.Column(db.String(255), nullable=True, server_default="N/A")
    # is_available = db.Column(db.Boolean , default = True)

    transactions = db.relationship('Transaction', back_populates='book')
    borrowed_books = db.relationship('BorrowedBook', back_populates='book')
    requests = db.relationship('RequestBook', back_populates='book')  
    return_books = db.relationship('ReturnBook', back_populates='book') 

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'authors': self.authors,
            'published_date': self.published_date,
            'isbn': self.isbn,
            'image_links': self.image_links
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'  # Changed to plural for consistency

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    time_stamp = db.Column(db.DateTime(timezone=True), default=func.now())
    transaction_type = db.Column(db.String(20), nullable=False)
    late_fees = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="transactions")
    book = db.relationship("Book", back_populates="transactions")

class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_books'  # Changed to plural for consistency

    borrowed_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    is_returned = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="borrowed_books")
    book = db.relationship("Book", back_populates="borrowed_books")

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'borrow_date': self.borrow_date,
            'return_date': self.return_date,
            'title': self.book.title,
            'img': self.book.image_links
        }

class RequestBook(db.Model):
    __tablename__ = 'request_books'  # Changed to plural for consistency

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # values: 'pending', 'approved', 'rejected'
    request_date = db.Column(db.DateTime(timezone=True), default=func.now())

    user = db.relationship("User", back_populates="requests")
    book = db.relationship("Book", back_populates="requests")

    def to_dict(self):
        return{
            'request_id':self.request_id,
            'user_id':self.user_id,
            'book_id':self.book_id
        }

class ReturnBook(db.Model):
    __tablename__ = 'return_books'  # Changed to plural for consistency

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # values: 'pending', 'approved', 'rejected'
    request_date = db.Column(db.DateTime(timezone=True), default=func.now())

    user = db.relationship("User", back_populates="return_books")
    book = db.relationship("Book", back_populates="return_books") 

    def to_dict(self):
        return{
            'request_id':self.request_id,
            'user_id':self.user_id,
            'book_id':self.book_id
        }
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Text 


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Consistent with table naming
    user_id = db.Column(db.Integer, primary_key=True)  # Assuming autoincrement
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    password_hash = db.Column(db.String(128))
    has_set_password = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'librarian', 'user')"),
    )

    transactions = db.relationship('Transaction', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.has_set_password = True

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __init__(self, email, first_name, last_name):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role='admin'
    def get_id(self):
        return str(self.user_id)
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_librarian(self):
        return self.role == 'librarian'



class Profile(db.Model):
    __tablename__ = 'profiles'  # Consistent with table naming
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Assuming autoincrement
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    profile_picture = db.Column(db.String(255))  
    birthdate = db.Column(db.Date)
    website = db.Column(db.String(255))


class Book(db.Model):  # Singular for the class name
    # id,etag,title,authors,publishedDate,description,pageCount,printType,maturityRating,imageLinks,language,previewLink,textSnippet,ISBN_10,ISBN_13,genre
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Assuming autoincrement
    isbn = db.Column(db.String(13), unique=True)  
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False) 
    publisher = db.Column(db.String(100))            
    publishDate = db.Column(db.String(20))                    
    genre = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    description = db.Column(Text)                     
    page_count = db.Column(db.Integer)                
    language = db.Column(db.String(50))

    transactions = db.relationship('Transaction', back_populates='book')


class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)  # Changed to 'books'
    checkout_date = db.Column(db.DateTime(timezone=True), default=func.now())
    due_date = db.Column(db.DateTime(timezone=True), nullable=False)
    return_date = db.Column(db.DateTime(timezone=True))
    late_fees = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="transactions")
    book = db.relationship("Book", back_populates="transactions")  # Changed to 'Book'


class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'  # Consistent with table naming
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)  # Changed to 'books'
    borrow_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    is_returned = db.Column(db.Boolean, default=False)

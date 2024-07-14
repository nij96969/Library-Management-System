import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # This allows OAuth to work with HTTP
import pandas as pd
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth import auth
from routes.main import main
from routes.profile import profile
from models import Book
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(profile)

@app.cli.command("drop-db")
def drop_db():
    """Drops database """
    with app.app_context():
        db.drop_all()
        # db.create_all()
        print("Database dropped")

@app.cli.command("add-books-pd")
def add_books_pd():
    df = pd.read_csv('books_data.csv')
    df = df.dropna()  # Remove rows with missing values (optional)
    df['authors']=df['authors'].astype(str)
    with db.session.begin():
        for _, row in df.iterrows():

            # Check if the book already exists based on ISBN
            existing_book = Book.query.filter_by(isbn=str(int(row['ISBN_13']))).first()

            if existing_book:
                # If exists, update quantity
                existing_book.quantity += 1
                existing_book.available += 1
            else:
                # Handle potential date format issues
                try:
                    if '-' in row['publishedDate']:
                        publish_date = datetime.strptime(row['publishedDate'], '%Y-%m-%d').date()
                    else:
                        publish_date = datetime.strptime(row['publishedDate'], '%Y').date()
                except ValueError:
                    publish_date = None  # Or set a default date

                # Data Preparation and Type Conversion

                book_data = {
                    'isbn': str(int(row['ISBN_13'])),
                    'title': row['title'],
                    'author': row['authors'],
                    'publishDate': publish_date, 
                    'description': row['description'],
                    'page_count': int(row['pageCount']),
                    'language': row['language'],
                    'image_url': row['imageLinks'],
                    'quantity': 1, 
                    'available': 1 
                }

                new_book = Book(**book_data)
                db.session.add(new_book)

        db.session.commit()

    print("Books added/updated successfully!")
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

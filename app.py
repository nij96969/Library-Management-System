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
from routes.admin import admin
from routes.librarian import librarian
from models import Book
from datetime import datetime
from flask import render_template, request
from model import get_book_recommendations



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
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(librarian, url_prefix='/librarian')

@app.cli.command("drop-db")
def drop_db():
    """Drops database """
    with app.app_context():
        db.drop_all()
        print("Database dropped")

@app.cli.command("add-books-pd")
def add_books_pd():
    df = pd.read_csv('books_data.csv')
    df = df.dropna()  # Remove rows with missing values (optional)
    df['authors'] = df['authors'].astype(str)
    with db.session.begin():
        count=0
        for _, row in df.iterrows():
            count+=1
            if(count>100):
                break
            if Book.query.filter_by(isbn=str(int(row['ISBN_13']))).first():
                print("book already exists")
            else:
                try:
                    if '-' in row['publishedDate']:
                        publish_date = datetime.strptime(row['publishedDate'], '%Y-%m-%d').date()
                    else:
                        publish_date = datetime.strptime(row['publishedDate'], '%Y').date()
                except ValueError:
                    publish_date = None
                # id,etag,title,authors,publishedDate,description,pageCount,printType,maturityRating,imageLinks,language,previewLink,textSnippet,ISBN_10,ISBN_13,genre
                book_data = {
                    'isbn': str(int(row['ISBN_13'])),
                    'title': row['title'],
                    'author': row['authors'],
                    'publisher':row['authors'],
                    'publishDate': row['publishedDate'], 
                    'description': row['description'],
                    'page_count': int(row['pageCount']),
                    'language': row['language'],
                    'image_url': row['imageLinks'],
                    'genre': row['genre'],
                    'language':row['language'] 
                }

                new_book = Book(**book_data)
                db.session.add(new_book)

        db.session.commit()

    print("Books added/updated successfully!")
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    recommendations = get_book_recommendations(search_query)
    if isinstance(recommendations, str):  # Handle error message
        recommendations = []
    return render_template('user_home.html', recommendations=recommendations)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
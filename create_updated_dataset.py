from app import create_app, db
from app.models import Book
import pandas as pd
def query_books():
    # Create an application context to interact with the database
    app = create_app()
    with app.app_context():
        # Query all books
        books = Book.query.all()
    
        
        # Convert query results into a list of dictionaries
        books_data = []
        for book in books:
            books_data.append({
                'book_id': book.book_id,
                'isbn': book.isbn,
                'title': book.title,
                'authors': book.authors,
                'published_date': book.published_date,
                'description': book.description,
                'page_count': book.page_count,
                'maturity_rating': book.maturity_rating,
                'image_links': book.image_links,
                'language': book.language,
                'categories': book.categories
            })
        
        # Convert list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(books_data)
        
        return df

if __name__ == "__main__":
    df = query_books()
    print(df)

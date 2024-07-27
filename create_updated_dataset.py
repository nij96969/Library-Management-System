from app import create_app
from app.models import Book
import pandas as pd
import requests , json

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
                'title': book.title,
                'authors': book.authors,
                'description': book.description,
            })
        
        # Convert list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(books_data)
        
        return df

if __name__ == "__main__":
    
    df = query_books()

    # Convert DataFrame to JSON
    data_json = df.to_dict(orient='records')
    
    response = requests.post('http://localhost:8000/update_data', 
                             json={'data': data_json})
    print(response.json())
    # print(df)

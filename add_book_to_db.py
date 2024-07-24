import csv
from app.models import Book
from app import db, create_app

def import_books(csv_file):
    app = create_app()
    with app.app_context():
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                page_count = row.get('pageCount', 0)
                try:
                    page_count = int(page_count)
                except ValueError:
                    page_count = 0  # Default value if conversion fails
                
                book = Book(
                    isbn=row.get('ISBN_13', "N/A"),
                    title=row.get('title', "N/A"),
                    authors=row.get('authors', "N/A"),
                    published_date=row.get('publishedDate', "N/A"),
                    description=row.get('description', "N/A"),
                    page_count=page_count,
                    maturity_rating=row.get('maturityRating', "N/A"),
                    image_links=row.get('imageLinks', "N/A"),
                    language=row.get('language', "N/A"),
                    categories=row.get('categories', "N/A")
                )
                db.session.add(book)
            db.session.commit()

if __name__ == '__main__':
    import_books(r'D:\Development Project\Library Management System\Dataset\books_set.csv')

import pandas as pd

# Read the CSV file into a DataFrame (ensure the filename is a string)
books_data = pd.read_csv('books_data.csv')

# Drop null values in `title`, `authors`, `description`, and other relevant columns
books_data_filtered = books_data.dropna(subset=['title', 'authors', 'description', 'publishedDate', 'imageLinks', 'ISBN_13']).reset_index(drop=True)

def get_book_recommendations(query):
    # Convert the query to lowercase for case-insensitive search
    query = query.lower()

    # Find books where the title contains the query
    matching_books = books_data_filtered[books_data_filtered['title'].str.lower().str.contains(query, na=False)]

    # Get the relevant details of the matching books
    recommendations = matching_books[['title', 'authors', 'publishedDate', 'imageLinks', 'ISBN_13']].to_dict('records')

    if not recommendations:
        return f"Error: No books found matching '{query}'."

    return recommendations

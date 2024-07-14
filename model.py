import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

# Read the CSV file into a DataFrame (ensure the filename is a string)
books_data = pd.read_csv('new_book_data.csv')

# Drop null values in `title`, `authors` and `description` columns
books_data_filtered = books_data.dropna(subset=['title', 'authors', 'description'])

# Combine features, preprocess
books_data_filtered['combined_features'] = books_data_filtered['title'] + ' ' + books_data_filtered['authors'] + ' ' + books_data_filtered['description']
books_data_filtered['combined_features'] = books_data_filtered['combined_features'].str.lower().apply(lambda x: re.sub(r'[^\w\s]', '', x)).apply(lambda x: x.split())

# TF-IDF Vectorization
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(books_data_filtered['combined_features'].apply(lambda x: ' '.join(x)))
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Simulated User-Item Matrix (Collaborative Filtering)
user_item_matrix = pd.DataFrame(0, index=range(10), columns=books_data_filtered['title'])
for index, row in books_data_filtered.iterrows():
    for word in row['combined_features']:
        user_item_matrix.loc[random.randint(0, 9), row['title']] += 1

item_sim = cosine_similarity(user_item_matrix.T)

# Hybrid Similarity
hybrid_sim = (cosine_sim + item_sim) / 2

# Set a default book title
default_book_title = 'Harry Potter and the Cursed Child'

# Get book title input from the user (with error handling)
try:
    book_title = input("Enter the title of a book for recommendations (or press Enter to use the default): ")
    if not book_title:  # Check if the user just pressed Enter
        book_title = default_book_title
except EOFError:
    print("EOFError occurred. Using default book title.")
    book_title = default_book_title

# Check if the book title exists in the dataset
if book_title not in books_data_filtered['title'].values:
    print(f"Error: The book '{book_title}' was not found in the dataset.")
else:
    # Get the index of the book in the filtered dataframe
    book_index = books_data_filtered[books_data_filtered['title'] == book_title].index[0]

    # Get the indices of the most similar books based on the hybrid similarity, including the input book itself
    similar_books = [(book_index, 1)] + list(enumerate(hybrid_sim[book_index]))
    sorted_similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)[:6]  # Get top 6 including the input book

    # Remove the first book (which is the input book itself)
    sorted_similar_books = sorted_similar_books[1:]

    # Print the titles of the top 5 most similar books
    print(f"\nTop 5 similar books to '{book_title}' (Hybrid Recommendation):")
    for i in sorted_similar_books:
        print(books_data_filtered.iloc[i[0]]['title'])

    # Print the indices of the top 5 most similar books in the original dataframe
    print(f"\nIndices of the top 5 similar books to '{book_title}' in the original dataframe:")
    for i in sorted_similar_books:
        original_index = books_data[books_data['title'] == books_data_filtered.iloc[i[0]]['title']].index[0]
        print(original_index)

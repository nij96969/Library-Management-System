import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import re
import joblib
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

# Remove the DataUpdateRequest class as we won't need it anymore
app = FastAPI()

# Global variables to store precomputed data
df_filtered = None
hybrid_sim = None
tfidf_vectorizer = None
tfidf_matrix = None

class BookRecommendationRequest(BaseModel):
    book_title: str

class DataUpdateRequest(BaseModel):
    data: List[Dict]  # List of dictionaries to represent the DataFrame rows

DATA_DIR = "data"
TFIDF_MATRIX_PATH = os.path.join(DATA_DIR, "tfidf_matrix.joblib")
TFIDF_VECTORIZER_PATH = os.path.join(DATA_DIR, "tfidf_vectorizer.joblib")
DF_FILTERED_PATH = os.path.join(DATA_DIR, "df_filtered.joblib")
HYBRID_SIM_PATH = os.path.join(DATA_DIR, "hybrid_sim.joblib")

def preprocess_data(books_data):
    global df_filtered, hybrid_sim, tfidf_vectorizer, tfidf_matrix

    df_filtered = books_data.dropna(subset=['title', 'authors', 'description'])
    df_filtered['combined_features'] = df_filtered['title'] + ' ' + df_filtered['authors'] + ' ' + df_filtered['description']
    df_filtered['combined_features'] = df_filtered['combined_features'].str.lower()
    df_filtered['combined_features'] = df_filtered['combined_features'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    df_filtered['combined_features'] = df_filtered['combined_features'].apply(lambda x: x.split())

    # TF-IDF Vectorization
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_filtered['combined_features'].apply(lambda x: ' '.join(x)))
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Create user-item matrix
    user_item_matrix = pd.DataFrame(0, index=range(10), columns=df_filtered['title'])
    for index, row in df_filtered.iterrows():
        for word in row['combined_features']:
            user_item_matrix.loc[random.randint(0, 9), row['title']] += 1

    # Calculate item-item similarity
    item_sim = cosine_similarity(user_item_matrix.T)

    # Combine similarities
    hybrid_sim = (cosine_sim + item_sim) / 2

    # Save computed data
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    joblib.dump(tfidf_matrix, TFIDF_MATRIX_PATH)
    joblib.dump(tfidf_vectorizer, TFIDF_VECTORIZER_PATH)
    joblib.dump(df_filtered, DF_FILTERED_PATH)
    joblib.dump(hybrid_sim, HYBRID_SIM_PATH)

@app.on_event("startup")
async def startup_event():
    global df_filtered, hybrid_sim, tfidf_vectorizer, tfidf_matrix

    if os.path.exists(TFIDF_MATRIX_PATH) and os.path.exists(TFIDF_VECTORIZER_PATH) and \
       os.path.exists(DF_FILTERED_PATH) and os.path.exists(HYBRID_SIM_PATH):
        # Load precomputed data
        tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
        tfidf_vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
        df_filtered = joblib.load(DF_FILTERED_PATH)
        hybrid_sim = joblib.load(HYBRID_SIM_PATH)
    else:
        # If precomputed data doesn't exist, load and preprocess the initial data
        books_data = pd.read_csv("books_set.csv")
        preprocess_data(books_data)

# @app.post("/recommend")
# async def recommend_books(request: BookRecommendationRequest):
#     global df_filtered, hybrid_sim

#     book_title = request.book_title
#     try:
#         book_index = df_filtered[df_filtered['title'] == book_title].index[0]
#     except IndexError:
#         raise HTTPException(status_code=404, detail=f"Book '{book_title}' not found in the database.")

#     similar_books = list(enumerate(hybrid_sim[book_index]))
#     sorted_similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)[1:6]

#     recommendations = [df_filtered.iloc[i[0]]['title'] for i in sorted_similar_books]
    
#     return {"recommendations": recommendations}


@app.post("/recommend")
async def recommend_books(request: BookRecommendationRequest):
    global df_filtered, hybrid_sim

    book_title = request.book_title
    try:
        book_index = df_filtered[df_filtered['title'] == book_title].index[0]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Book '{book_title}' not found in the database.")

    similar_books = list(enumerate(hybrid_sim[book_index]))
    sorted_similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)[1:6]

    recommendations = [
        {
            'book_id': int(df_filtered.iloc[i[0]]['book_id']),
            'title': df_filtered.iloc[i[0]]['title']
        }
        for i in sorted_similar_books
    ]
    
    return {"recommendations": recommendations}


@app.post("/update_data")
async def update_data(request: DataUpdateRequest):
    try:

        # Convert the list of dictionaries to a DataFrame
        new_books_data = pd.DataFrame(request.data)
        
        # Print or log the DataFrame for debugging
        # print(new_books_data.shape)
        preprocess_data(new_books_data)
        return {"message": "Data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

class MovieRecommender:
    def __init__(self, data_path='movies.csv'):
        self.df = pd.read_csv(data_path)
        self._prepare_data()
        self._compute_similarity()

    def _prepare_data(self):
        # We'll combine genres and overview to create a solid 'tags' column for our content-based matching
        self.df['genres'] = self.df['genres'].fillna('')
        self.df['overview'] = self.df['overview'].fillna('')
        self.df['poster_path'] = self.df['poster_path'].fillna('https://placehold.co/400x600/0f172a/38bdf8?text=Poster+Unavailable')
        
        # Combine them into a single string for each movie
        self.df['combined_features'] = self.df['genres'] + " " + self.df['overview']
        
        # Clean text slightly
        self.df['combined_features'] = self.df['combined_features'].apply(lambda x: re.sub('[^a-zA-Z\s]', '', str(x).lower()))

    def _compute_similarity(self):
        # Using TF-IDF to find important words and give them weight
        cv = TfidfVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(self.df['combined_features'])
        
        # Compute cosine similarity
        self.similarity = cosine_similarity(vectors)

    def _format_movie(self, row):
        return {
            "id": int(row['id']),
            "title": row['title'],
            "genres": row['genres'],
            "overview": row['overview'][:120] + '...' if len(row['overview']) > 120 else row['overview'],
            "rating": float(row['vote_average']),
            "poster": row['poster_path']
        }

    def get_recommendations(self, movie_title, num_recommendations=6):
        try:
            # Case insensitive exact match or closest match
            movie_matches = self.df[self.df['title'].str.contains(movie_title, case=False, regex=False)]
            if movie_matches.empty:
                return {"error": "Movie not found in the database. Please try another one."}
            
            movie_index = movie_matches.index[0]
            
            # Get similarity scores for this movie
            distances = self.similarity[movie_index]
            
            # Sort movies based on similarity score, ignoring the first one (itself)
            movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations+1]
            
            recommended_movies = []
            for i in movies_list:
                similar_movie = self.df.iloc[i[0]]
                recommended_movies.append(self._format_movie(similar_movie))
                
            return {
                "search_term": self.df.iloc[movie_index]['title'],
                "recommendations": recommended_movies
            }
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def filter_and_sort_movies(self, genre=None, min_rating=0, sort_by=None, limit=12):
        try:
            # Start with full dataset
            filtered_df = self.df.copy()
            
            # 1. Apply Genre Filter
            if genre and genre != "All":
                filtered_df = filtered_df[filtered_df['genres'].str.contains(genre, case=False, na=False)]
                
            # 2. Apply Rating Filter
            if min_rating > 0:
                filtered_df = filtered_df[filtered_df['vote_average'] >= min_rating]
                
            # 3. Apply Sorting
            if sort_by == 'rating_desc':
                filtered_df = filtered_df.sort_values(by='vote_average', ascending=False)
            elif sort_by == 'rating_asc':
                filtered_df = filtered_df.sort_values(by='vote_average', ascending=True)
            elif sort_by == 'title_asc':
                filtered_df = filtered_df.sort_values(by='title', ascending=True)
            elif sort_by == 'title_desc':
                filtered_df = filtered_df.sort_values(by='title', ascending=False)
            else:
                # Default behavior: Random sample if no sort provided, else take top from filtered list
                pass 
                
            # Limit results or randomise if no specific sorting requested
            if len(filtered_df) > limit:
                if not sort_by or sort_by == 'random':
                    filtered_df = filtered_df.sample(limit)
                else:
                    filtered_df = filtered_df.head(limit)
            elif len(filtered_df) == 0:
                 return []
                 
            # Format output
            movies = []
            for _, row in filtered_df.iterrows():
                movies.append(self._format_movie(row))
                
            return movies
        except Exception as e:
            print("Error filtering:", e)
            return []

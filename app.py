from flask import Flask, request, jsonify, render_template
from recommender import MovieRecommender

app = Flask(__name__)

# Initialize the recommender engine
print("Loading enhanced movie dataset and training recommendation model...")
recommender = MovieRecommender('movies.csv')
print("Model ready!")

@app.route('/')
def home():
    # Render the main HTML page
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        movie_title = data.get('title', '')
        
        if not movie_title:
            return jsonify({"error": "Please provide a movie title."}), 400
            
        result = recommender.get_recommendations(movie_title, num_recommendations=6)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/discover', methods=['POST', 'GET'])
def discover():
    try:
        # Default empty parameters
        genre = None
        min_rating = 0
        sort_by = "random"
        
        # If POST request, extract JSON body parameters for filters
        if request.method == 'POST':
            data = request.get_json()
            if data:
                genre = data.get('genre', "All")
                min_rating = float(data.get('min_rating', 0))
                sort_by = data.get('sort_by', "random")

        # Execute filter backend logic
        movies = recommender.filter_and_sort_movies(
            genre=genre, 
            min_rating=min_rating, 
            sort_by=sort_by, 
            limit=12
        )
        
        return jsonify({"recommendations": movies})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

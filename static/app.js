document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const searchInput = document.getElementById('movie-search');
    const searchBtn = document.getElementById('search-btn');
    const movieGrid = document.getElementById('movie-grid');
    const resultsTitle = document.getElementById('results-title');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-message');
    
    // Filter Elements
    const genreFilter = document.getElementById('genre-filter');
    const sortFilter = document.getElementById('sort-filter');
    const ratingFilter = document.getElementById('rating-filter');
    const ratingValText = document.getElementById('rating-val');

    // Currently active mode ('discover' or 'recommend')
    let currentMode = 'discover'; 

    // Initial Load
    applyFilters();

    // Event Listeners for Search
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Event Listeners for Filters
    genreFilter.addEventListener('change', applyFilters);
    sortFilter.addEventListener('change', applyFilters);
    
    ratingFilter.addEventListener('input', (e) => {
        ratingValText.textContent = e.target.value;
    });
    
    ratingFilter.addEventListener('change', (e) => {
        // Triggered when slider interaction ends
        applyFilters();
    });
    
    searchInput.addEventListener('input', (e) => {
        // If user clears the search, automatically jump back to filter mode
        if (e.target.value.trim() === '') {
            applyFilters();
        }
    });

    function applyFilters() {
        currentMode = 'discover';
        
        const filters = {
            genre: genreFilter.value,
            sort_by: sortFilter.value,
            min_rating: parseFloat(ratingFilter.value)
        };
        
        loader.classList.add('active');
        movieGrid.innerHTML = '';
        
        // Update Title contextually
        if(filters.genre === 'All' && filters.min_rating === 0 && filters.sort_by === 'random') {
             resultsTitle.textContent = "Discover Curated Masterpieces";
        } else {
             resultsTitle.textContent = `Filtered Results`;
        }

        fetch('/api/discover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        })
        .then(response => response.json())
        .then(data => {
            loader.classList.remove('active');
            if (data.recommendations) {
                renderMovies(data.recommendations);
            } else if (data.error) {
                showError(data.error);
            }
        })
        .catch(err => {
            loader.classList.remove('active');
            console.error("Error fetching discover movies:", err);
            showError("Network Error. Check console.");
        });
    }

    function handleSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            showError("Please enter a movie title.");
            return;
        }

        currentMode = 'recommend';
        hideError();
        loader.classList.add('active');
        movieGrid.innerHTML = '';
        resultsTitle.textContent = "Analyzing Cinematic Patterns...";

        fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify({ title: query })
        })
        .then(response => response.json())
        .then(data => {
            loader.classList.remove('active');
            
            if (data.error) {
                showError(data.error);
                resultsTitle.textContent = "Something went wrong";
                return;
            }

            resultsTitle.textContent = `Because you like "${data.search_term}"`;
            renderMovies(data.recommendations);
            
            // Optionally, reset filters in UI to avoid confusion
            genreFilter.value = 'All';
            sortFilter.value = 'random';
            ratingFilter.value = '0';
            ratingValText.textContent = '0';
            
        })
        .catch(err => {
            loader.classList.remove('active');
            showError("Failed to connect to the recommendation engine.");
            console.error(err);
        });
    }

    function renderMovies(movies) {
        movieGrid.innerHTML = '';
        
        if (!movies || movies.length === 0) {
            movieGrid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; padding: 3rem; color: var(--text-secondary); font-size: 1.1rem; border: 1px dashed var(--card-border); border-radius: 12px;">No movies match your current filters. Try relaxing the rating or changing the genre!</p>';
            return;
        }

        movies.forEach((movie, index) => {
            const delay = index * 0.05; // Slightly faster stagger
            
            const card = document.createElement('div');
            card.className = 'movie-card';
            card.style.animationDelay = `${delay}s`;
            
            card.innerHTML = `
                <div class="card-image-wrap">
                    <img src="${movie.poster}" alt="${movie.title} poster" class="movie-poster" loading="lazy" onerror="this.src='https://placehold.co/400x600/0f172a/38bdf8?text=Image+Not+Found'">
                    <div class="rating-badge">
                        <i class="ti ti-star-filled"></i> ${movie.rating.toFixed(1)}
                    </div>
                </div>
                <div class="card-content">
                    <h3 class="movie-title">${movie.title}</h3>
                    <div class="movie-genres">${movie.genres}</div>
                    <p class="movie-desc">${movie.overview}</p>
                </div>
            `;
            
            movieGrid.appendChild(card);
        });
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.add('visible');
        setTimeout(() => {
            errorMsg.classList.remove('visible');
        }, 5000);
    }

    function hideError() {
        errorMsg.textContent = '';
        errorMsg.classList.remove('visible');
    }
});

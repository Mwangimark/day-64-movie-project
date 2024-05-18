import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year_made = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    ranking = db.Column(db.String, nullable=False)


# functions
def fetch_and_save_movie_details():
    api_key = 'YOUR_API_KEY'
    url = "https://api.themoviedb.org/3/movie/popular"

    params = {
        "api_key": api_key,
        "language": "en-US",
        "page": 1
    }

    response = requests.get(url=url, params=params)
    response.raise_for_status()

    data = response.json()
    movies = data.get('results', [])

    for movie_data in movies:
        title = movie_data.get('original_title', '')
        description = movie_data.get('overview', '')
        img_path = movie_data.get('poster_path', '')
        img_url = f"https://image.tmdb.org/t/p/w500{img_path}" if img_path else ''
        year = int(movie_data.get('release_date', '').split('-')[0]) if movie_data.get('release_date', '') else None
        ranking = movie_data.get('vote_average', 0)

        existing_movie = Movie.query.filter_by(title=title).first()

        if not existing_movie:
            movie = Movie(title=title, description=description, img_url=img_url, year_made=year, ranking=ranking)
            db.session.add(movie)
            print("movie_added")

    db.session.commit()


#     functions urls
@app.route('/')
def home():
    all_movies = Movie.query.all()
    return render_template('index.html', all_movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit_rank():
    if request.method == "POST":
        movie_id = request.args.get('id')
        movie_selected = Movie.query.filter_by(id=movie_id).first()
        selected_rank = request.form.get('rank')
        movie_selected.ranking = float(selected_rank)
        db.session.commit()
        return redirect(url_for('home'))

    movie_id = request.args.get('id')
    movie_selected = Movie.query.filter_by(id=movie_id).first()
    return render_template('edit.html', movie_selected=movie_selected)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.filter_by(id=movie_id).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


with app.app_context():
    db.create_all()
    fetch_and_save_movie_details()

if __name__ == '__main__':
    app.run(debug=True)

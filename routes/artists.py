from flask import (Blueprint, render_template,
                   request, flash, redirect, url_for)
from sqlalchemy import func
from forms import *
from flask import abort
from models import *
artists_bp = Blueprint('artists_bp', __name__)


@artists_bp.route('/artists')
def artists():
    data = []

    artists_data = db.session.query(Artist, func.count(Show.id)).outerjoin(
        Show).filter(Show.start_time > datetime.now()).group_by(Artist).all()

    for artist, num_upcoming_shows in artists_data:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })

    return render_template('pages/artists.html', artists=data)


@artists_bp.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(func.lower(Artist.name).contains(
        search_term.lower())).all()
    data = []

    for artist in artists:
        num_upcoming_shows = Show.query.filter(
            Show.artist_id == artist.id, Show.start_time > datetime.now()).count()

        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming_shows
            }

        )
    response = {"count": len(artists), "data": data}

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@artists_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.get(Artist, artist_id)

    upcoming_shows = db.session.query(Venue, Show).join(Show).filter(
        Show.artist_id == artist_id, Show.start_time > datetime.now()).all()
    past_shows = db.session.query(Venue, Show).join(Show).filter(
        Show.artist_id == artist_id, Show.start_time <= datetime.now()).all()

    artist: Artist
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.phone,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
        "upcoming_shows": [{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


@artists_bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist: Artist = db.session.get(Artist, artist_id)

    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@artists_bp.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = db.session.get(Artist, artist_id)
    if form.validate():
        try:
            artist.name = form.name.data
            artist.genres = form.genres.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website = form.website_link.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue = bool(form.seeking_venue.data)
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)

    return redirect(url_for('artists_bp.show_artist', artist_id=artist_id))


@artists_bp.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@artists_bp.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    if form.validate():
        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data
            )

            with app.app_context():
                db.session.add(new_artist)
                db.session.commit()

             # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except Exception as e:
            with app.app_context():
                db.session.rollback()
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
            print(e)
            abort(500)
        finally:
            with app.app_context():
                db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)

    return render_template('pages/home.html')

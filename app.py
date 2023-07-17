# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func
from forms import *
from flask import abort
from models import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
    venue: Venue
    for venue in venues:
        upcoming_shows = Show.query.filter(
            Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": upcoming_shows}]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(func.lower(Venue.name).contains(
        search_term.lower())).all()
    data = []
    venue: Venue
    for venue in venues:
        upcoming_shows = Show.query.filter(
            Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.get(Venue, venue_id)
    upcoming_shows = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time > datetime.now()).all()
    past_shows = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time <= datetime.now()).all()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    if form.validate():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data
            )

            with app.app_context():
                db.session.add(new_venue)
                db.session.commit()

            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except Exception as e:
            with app.app_context():
                db.session.rollback()
            flash('An error occurred. Venue ' +
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

    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue with ID ' + str(venue_id) + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue with ID ' +
              str(venue_id) + ' could not be deleted.')
        abort(500)
    finally:
        db.session.close()
    return redirect(url_for('venues'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.all()

    data = []
    artist: Artist
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
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


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.get(Artist, artist_id)

    upcoming_shows = Show.query.filter(
        Show.artist_id == artist_id, Show.start_time > datetime.now()).all()
    past_shows = Show.query.filter(
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
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
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


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
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

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue: Venue = db.session.get(Venue, venue_id)

    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = db.session.get(Venue, venue_id)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.address = form.address.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.website = form.website_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            abort(500)
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
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


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = Show.query.all()

    show: Show
    venue: Venue
    artist: Artist
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    if form.validate():
        try:
            new_show = Show(
                id=form.artist_id.data,
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data
            )

            with app.app_context():
                db.session.add(new_show)
                db.session.commit()

             # on successful db insert, flash success
            flash('Show ' + request.form['artist_id'] +
                  ' was successfully listed!')

        except Exception as e:
            with app.app_context():
                db.session.rollback()
            flash('An error occurred. Show ' +
                  request.form['artist_id'] + ' could not be listed.')
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


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

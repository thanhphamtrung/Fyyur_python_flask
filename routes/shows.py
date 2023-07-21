from flask import (Blueprint, render_template,
                   request, flash)
from flask import abort

from forms import *
from models import *

shows_bp = Blueprint('shows_bp', __name__)


@shows_bp.route('/shows')
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


@shows_bp.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@shows_bp.route('/shows/create', methods=['POST'])
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

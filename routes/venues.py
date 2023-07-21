from flask import (Blueprint, render_template,
                   request, flash, redirect, url_for)
from sqlalchemy import func
from forms import *
from flask import abort
from models import *

venues_bp = Blueprint('venues_bp', __name__)


@venues_bp.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
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


@venues_bp.route('/venues/search', methods=['POST'])
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


@venues_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).all()

    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).all()

    Show.query.filter(
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
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


@venues_bp.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@venues_bp.route('/venues/create', methods=['POST'])
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


@venues_bp.route('/venues/<int:venue_id>', methods=['DELETE'])
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
    return redirect(url_for('venues_bp.venues'))

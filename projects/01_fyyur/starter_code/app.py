#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from itertools import groupby
from operator import attrgetter
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type = True)

from models import *

#----------------------------------------------------------------------------#
# Utils.
#----------------------------------------------------------------------------#

def is_valid_venue(venue_id):
  venue = Venue.query.get(venue_id)
  return venue is not None

def is_valid_artist(artist_id):
  artist = Artist.query.get(artist_id)
  return artist is not None

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  all_venues = Venue.query.order_by(Venue.state, Venue.city).all()
  data = [
    {
      'state': state,
      'city': city,
      'venues': list(venue_list)
    } for (state, city), venue_list in groupby(all_venues, attrgetter('state', 'city'))
  ]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  data = Venue.query \
              .filter(Venue.name \
                           .ilike(f'%{search_term}%')) \
              .all()
  
  return render_template('pages/search_venues.html',
                          results={
                            'count': len(data),
                            'data': data
                          },
                          search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  venue.upcoming_shows = venue.get_upcoming_shows()
  venue.upcoming_shows_count = len(venue.upcoming_shows)
  venue.past_shows = venue.get_past_shows()
  venue.past_shows_count = len(venue.past_shows)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    new_venue = Venue(name = request.form['name'],
                      image_link = request.form['image_link'],
                      city = request.form['city'],
                      state = request.form['state'],
                      address = request.form['address'],
                      phone = request.form['phone'],
                      genres = request.form.getlist('genres'),
                      facebook_link = request.form['facebook_link'])
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    flash('Venue ' + venue.name + ' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query
                                                             .order_by('id')
                                                             .all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  data = Artist.query \
               .filter(Artist.name \
                             .ilike(f'%{search_term}%')) \
               .all()

  return render_template('pages/search_artists.html',
                          results={
                            'count': len(data),
                            'data': data
                          },
                          search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist.upcoming_shows = artist.get_upcoming_shows()
  artist.upcoming_shows_count = len(artist.upcoming_shows)
  artist.past_shows = artist.get_past_shows()
  artist.past_shows_count = len(artist.past_shows)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  
  if artist is None:
    flash(f'Artist with ID {artist_id}does not exist.')
    return redirect(url_for('index'))

  form = ArtistForm()
  form.name.data = artist.name
  form.image_link.data = artist.image_link
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link

  return render_template('forms/edit_artist.html',
                          form=form,
                          artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.image_link = request.form['image_link']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  
  if venue is None:
    flash(f'Venue with ID {venue_id}does not exist.')
    return redirect(url_for('index'))

  form = VenueForm()
  form.name.data = venue.name
  form.image_link.data = venue.image_link
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link

  return render_template('forms/edit_venue.html',
                          form=form,
                          venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  return render_template('forms/new_artist.html',
                          form=ArtistForm())

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    new_artist = Artist(name = request.form['name'],
                        image_link = request.form['image_link'],
                        city = request.form['city'],
                        state = request.form['state'],
                        phone = request.form['phone'],
                        genres = request.form.getlist('genres'),
                        facebook_link = request.form['facebook_link'])
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  if not is_valid_artist(request.form['artist_id']):
    flash('The specified artist does not exist!')
    return render_template('forms/new_show.html', form = ShowForm())

  if not is_valid_venue(request.form['venue_id']):
    flash('The specified venue does not exist!')
    return render_template('forms/new_show.html', form = ShowForm())

  try:
    new_show = Show(artist_id = request.form['artist_id'],
                    venue_id = request.form['venue_id'],
                    start_time = request.form['start_time'])
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error ocurred and the show could not be listed.')
  finally:
    db.session.close()

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

from datetime import datetime
from app import db

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(100)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venue', lazy = True)

    def get_upcoming_shows(self):
      data = []

      for show in self.shows:
        if (show.start_time < datetime.utcnow()):
          continue

        artist = Artist.query.get(show.artist_id)
        data.append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time
        })
        
      return data

    def get_past_shows(self):
      data = []

      for show in self.shows:
        if (show.start_time >= datetime.utcnow()):
          continue

        artist = Artist.query.get(show.artist_id)
        data.append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time
        })
        
      return data

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(100)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artist', lazy = True)

    def get_upcoming_shows(self):
      data = []

      for show in self.shows:
        if (show.start_time < datetime.utcnow()):
          continue

        venue = Venue.query.get(show.venue_id)
        data.append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        })
        
      return data

    def get_past_shows(self):
      data = []

      for show in self.shows:
        if (show.start_time >= datetime.utcnow()):
          continue

        venue = Venue.query.get(show.venue_id)
        data.append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        })
        
      return data

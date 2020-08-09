from datetime import datetime
from app import db

show = db.Table('show',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('start_time', db.DateTime, nullable = False, primary_key=True)
)

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

    shows = db.relationship('Artist', secondary = show, backref = db.backref('shows', lazy = True))

    @staticmethod
    def parse_show_results(show_list):
      data = []

      for show in show_list:
        artist = Artist.query.get(show.artist_id)
        data.append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time
        })
        
      return data

    def get_upcoming_shows(self):
      result = db.session.query(show)                                    \
                         .filter(show.c.venue_id == self.id,             \
                                  datetime.utcnow() < show.c.start_time) \
                         .all()
      return Venue.parse_show_results(result)

    def get_past_shows(self):
      result = db.session.query(show)                                    \
                         .filter(show.c.venue_id == self.id,             \
                                  datetime.utcnow() > show.c.start_time) \
                         .all()
      return Venue.parse_show_results(result)

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

    @staticmethod
    def parse_show_results(show_list):
      data = []

      for show in show_list:
        venue = Venue.query.get(show.venue_id)
        data.append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        })
        
      return data

    def get_upcoming_shows(self):
      result = db.session.query(show)                                    \
                         .filter(show.c.artist_id == self.id,             \
                                  datetime.utcnow() < show.c.start_time) \
                         .all()
      return Artist.parse_show_results(result)

    def get_past_shows(self):
      result = db.session.query(show)                                    \
                         .filter(show.c.artist_id == self.id,             \
                                  datetime.utcnow() > show.c.start_time) \
                         .all()
      return Artist.parse_show_results(result)

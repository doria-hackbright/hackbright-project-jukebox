"""Office Jukebox: Database models"""

# Flask and SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Other Libraries
import uuid


################################################################################
### (1) Model Definitions

db = SQLAlchemy()


class JukeboxAdmin(db.Model):
    """User that creates a jukebox (admin).

    Have the ability to control the music player, add/delete songs at will and
    to end a jukebox."""

    __tablename__ = "admin_users"

    admin_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jukebox_id = db.Column(db.String(64),
                           db.ForeignKey('jukeboxes.jukebox_id'),
                           nullable=False)

    @classmethod
    def create(cls, jukebox_id):
        """Create a new guest for a playlist."""

        new_admin = cls(jukebox_id=jukebox_id)

        db.session.add(new_admin)
        db.session.commit()

        return new_admin


class JukeboxGuest(db.Model):
    """Users with guest access to a given jukebox.

    They recieved a unique public URL to the jukebox from the admin user.
    Have the ability upvote/downvote songs and add songs to playlists."""

    __tablename__ = "guest_users"

    guest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jukebox_id = db.Column(db.String(64),
                           db.ForeignKey('jukeboxes.jukebox_id'),
                           nullable=False)

    @classmethod
    def create(cls, jukebox_id):
        """Create a new guest for a playlist."""

        new_guest = cls(jukebox_id=jukebox_id)

        db.session.add(new_guest)
        db.session.commit()

        return new_guest


class Jukebox(db.Model):
    """Jukebox with a music player and a crowd-controlled playlist."""

    __tablename__ = "jukeboxes"

    jukebox_id = db.Column(db.String(64),
                           nullable=False,
                           primary_key=True)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=db.func.current_timestamp())
    last_updated = db.Column(db.DateTime,
                             nullable=False,
                             server_default=db.func.now(),
                             onupdate=db.func.now())

    admin = db.relationship('JukeboxAdmin', backref='jukebox')
    guests = db.relationship('JukeboxGuest', backref='jukebox')
    relations = db.relationship('SongUserRelationship', backref='jukebox')
    songs = db.relationship('Song',
                            secondary='song_user_relations',
                            backref='jukeboxes')
    votes = db.relationship('Vote',
                            secondary='song_user_relations',
                            backref='jukeboxes')

    @classmethod
    def create(cls):
        """Create a new jukebox is a unique, URL-safe UUID."""

        jukebox_id = str(uuid.uuid4())

        new_jukebox = cls(jukebox_id=jukebox_id)

        db.session.add(new_jukebox)
        db.session.commit()

        return new_jukebox


class Song(db.Model):
    """Song from Spotify API."""

    __tablename__ = "songs"

    song_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_uri = db.Column(db.String(256), nullable=False)
    song_name = db.Column(db.String(256), nullable=False)
    song_artist = db.Column(db.String(256), nullable=True)
    song_album = db.Column(db.String(256), nullable=True)

    @classmethod
    def create(cls, spotify_uri, song_name, song_artist, song_album):
        """Add a new song to the database."""

        new_song = cls(spotify_uri=spotify_uri,
                       song_name=song_name,
                       song_artist=song_artist,
                       song_album=song_album)

        db.session.add(new_song)
        db.session.commit()

        return new_song


class Vote(db.Model):
    """An upvote/downvote from a guest user on a song in a jukebox."""

    __tablename__ = "votes"

    vote_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    song_user_id = db.Column(db.Integer,
                             db.ForeignKey('song_user_relations.song_user_id'),
                             nullable=False)
    voter_id = db.Column(db.Integer,
                         db.ForeignKey('guest_users.guest_id'),
                         nullable=False)
    vote_value = db.Column(db.Integer, nullable=False)

    @classmethod
    def create(cls, song_user_id, voter_id, vote_value):
        """Generate a new upvote/downvote."""

        new_vote = cls(song_user_id=song_user_id,
                       voter_id=voter_id,
                       vote_value=vote_value)

        db.session.add(new_vote)
        db.session.commit()

        return new_vote


class SongUserRelationship(db.Model):
    """Shows who added a song and when a song was added to a jukebox.

    Used to ensure guest users do not vote on their own songs.
    If a song was added by an administrator, the user_id field will be null."""

    __tablename__ = "song_user_relations"

    song_user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    song_id = db.Column(db.Integer,
                        db.ForeignKey('songs.song_id'),
                        nullable=False)
    jukebox_id = db.Column(db.String(64),
                           db.ForeignKey('jukeboxes.jukebox_id'),
                           nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('guest_users.guest_id'),
                        nullable=True)
    timestamp = db.Column(db.DateTime,
                          server_default=db.func.now(),
                          nullable=False)

    song = db.relationship('Song', backref="relations")
    votes = db.relationship('Vote', backref="relation")

    @classmethod
    def create(cls, song_id, jukebox_id, user_id):
        """Generate a new song/user relationship for jukebox."""

        new_relationship = cls(song_id=song_id,
                               jukebox_id=jukebox_id,
                               user_id=user_id)

        db.session.add(new_relationship)
        db.session.commit()

        return new_relationship


################################################################################
### (2) Setup Functions


def connect_to_db(app):
    """Connect the database to the Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///office-jukebox'

    # More verbose console output to check SQL queries
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)
    print "Connected to DB"


def init_app():
    """Create Flask app in order to use Flask-SQLAlchemy."""

    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)


if __name__ == "__main__":
    # For running in interactive mode

    init_app()

    # Creates the tables if they don't already exist when testing in -i mode
    db.create_all()

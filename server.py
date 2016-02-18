"""Office Jukebox: Server"""

# Standard Python Libraries
import os
import threading
import json

# Flask
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

# Tornado
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop

# Other External Libraries
import spotify
import requests

# Models (and Bottles)
from model import *


################################################################################
### (1) Setting up Flask app

app = Flask(__name__)


################################################################################
### (2) WebSocket Setup


class WebSocket(WebSocketHandler):

    connections = dict()

    def open(self):
        print "Socket connected!"

    def on_message(self, message):

        # Adding the connection to the set
        jukebox_id = json.loads(message)['jukebox_id']
        print jukebox_id

        if json.loads(message).get('first_load'):
            self.connections.setdefault(jukebox_id, set()).add(self)

            # Query for all the song relations for the playlist so far
            song_relationship_list = Jukebox.query.get(jukebox_id).relations

            # If there are existing relations, render the playlist for this connection
            if song_relationship_list:

                # Construct song_relationship dictionary
                for r in song_relationship_list:
                    playlist_row = {"song_name": r.song.song_name,
                                    "song_artist": r.song.song_artist,
                                    "song_album": r.song.song_album,
                                    "song_votes": 0}
                    self.write_message(playlist_row)

        # Write the update to all connections
        for c in self.connections[jukebox_id]:
            c.write_message(message)

    def on_close(self):

        print self.close_code, self.close_reason
        print "Socket disconnected!"


################################################################################
### (3) Supporting Functions


def spotify_login(session):
    """Logs into Spotify to access the features."""

    # Set up an event for "logged_in" and a listener for the connection state
    _logged_in = threading.Event()

    def _logged_in_listener(session):
        """A function that sets the logged in thread event to true."""

        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            _logged_in.set()

    # Set up Pyspotify event loop
    loop = spotify.EventLoop(session)
    loop.start()

    # Register event listener
    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED,
               _logged_in_listener)

    # Login using environment variables
    session.login(os.environ['SPOTIFY_UN'], os.environ['SPOTIFY_PW'])

    # Blocks the thread until the event becomes True, which will be triggered
    # by function connection_state_listener (success handler), attached to the
    # session event listener
    _logged_in.wait()

    print "#######################################"
    print "logged in: ", session.connection.state
    print "######################################"


################################################################################
### (4) App routes


@app.route("/")
def homepage():
    """Renders the homepage where users can create a jukebox.

    If someone is already a guest or admin user of a jukebox,
    it will take them to their respective jukebox pages instead."""

    jukebox_id = session.get('jukebox_id')

    if session.get('guest_id'):
        # if the user is already a guest of a jukebox
        return redirect(url_for('jukebox_public', jukebox_id=jukebox_id))

    elif session.get('admin_id'):
        # if the user is already an admint of a jukebox
        return redirect(url_for('jukebox_private', jukebox_id=jukebox_id))

    else:
        return render_template('homepage.html')


@app.route("/jukebox", methods=['POST'])
def new_jukebox():
    """Creates new jukebox and admin, adds to db, renders admin view."""

    new_jukebox = Jukebox.create()
    new_jukebox_id = new_jukebox.jukebox_id
    session['jukebox_id'] = new_jukebox_id

    new_user = JukeboxAdmin.create(jukebox_id=new_jukebox_id)
    session['admin_id'] = new_user.admin_id

    return redirect(url_for('jukebox_private', jukebox_id=new_jukebox_id))


@app.route("/jukebox/<jukebox_id>", methods=['GET'])
def jukebox_public(jukebox_id):
    """Renders the guest view for a jukebox."""

    return render_template('jukebox_guest.html')


@app.route("/jukebox/<jukebox_id>/admin", methods=['GET'])
def jukebox_private(jukebox_id):
    """Renders the admin view for a jukebox."""

    public_url = "localhost:5000/jukebox/" + jukebox_id
    url = "/jukebox/" + jukebox_id + "/delete"

    return render_template('jukebox_admin.html',
                           public_url=public_url,
                           url=url)


@app.route("/jukebox_id", methods=['GET'])
def jukebox_id():
    """Returns jukebox_id."""

    return session.get('jukebox_id')


@app.route("/guest_id", methods=['GET'])
def guest_id():
    """Returns guest_id."""

    return jsonify({"guest_id": session.get('guest_id')})
    # return session.get('guest_id', "no")


@app.route("/guest", methods=['POST'])
def new_guest():
    """Creates a new guest."""

    jukebox_id = request.form.get('jukebox_id')
    print jukebox_id

    if not session.get('guest_id'):
        new_user = JukeboxGuest.create(jukebox_id=jukebox_id)
        print new_user.guest_id
        session['guest_id'] = new_user.guest_id
        session['jukebox_id'] = jukebox_id

    return redirect(url_for('jukebox_public', jukebox_id=jukebox_id))


@app.route("/search", methods=['GET'])
def new_song():
    """Shows search resuts for songs."""

    # Retrieve the search term from the form
    search_term = request.args.get('search-term')
    print search_term

    # Use requests to make a call to Spotify Web API
    results = requests.get('https://api.spotify.com/v1/search?q=' +
                           search_term +
                           "&type=track&limit=10")

    return jsonify(results.json())


@app.route("/song/add", methods=['POST'])
def add_song_to_jukebox():
    """Adds a song chosen from the search to the jukebox and database"""

    # Pull the information that is being submitted
    song_uri = request.form.get('song-uri')
    song_name = request.form.get('song-name')
    song_artist = request.form.get('song-artist')
    song_album = request.form.get('song-album')

    # Check if the song is already in the database
    # If it is not there, add it
    if not Song.query.filter(Song.spotify_uri == song_uri).first():
        # Create a new song to add into the database
        new_song = Song.create(spotify_uri=song_uri,
                               song_name=song_name,
                               song_artist=song_artist,
                               song_album=song_album)

    else:
        new_song = Song.query.filter(Song.spotify_uri == song_uri).one()

    relation = SongUserRelationship.create(song_id=new_song.song_id,
                                           jukebox_id=session['jukebox_id'],
                                           user_id=session.get('guest_id'))

    # Construct song information
    response_dict = {"song_name": song_name,
                     "song_artist": song_artist,
                     "song_album": song_album,
                     "song_uri": song_uri,
                     "song_votes": 0,
                     "jukebox_id": session['jukebox_id'],
                     "guest_id": session.get('guest_id')}

    return jsonify(response_dict)


@app.route("/jukebox/<jukebox_id>/playlist", methods=['GET'])
def show_playlist(jukebox_id):
    """Render playlist for the specific jukebox."""

    # Query for a list of songs in the jukebox specific to that jukebox
    playlist = Jukebox.query.get(jukebox_id).relations
    print playlist

    # TODO:
    # Get their votes
    # Order songs in jukebox

    playlist_dict = {}

    # Send back JSON to render DOM on Javascript (the funnest)
    for r in playlist:
        song_id = r.song.spotify_uri[14:]
        song_data = requests.get("https://api.spotify.com/v1/tracks/" + song_id)
        print song_data.json()['name'], song_data.json()['artists'][0]['name']

    return jsonify(playlist_dict)


@app.route("/jukebox/<jukebox_id>/delete", methods=['POST'])
def delete_jukebox(jukebox_id):
    """Deletes a jukebox and all of its admin, guests, votes, and songs."""

    current_jukebox = Jukebox.query.get(jukebox_id)

    for vote in current_jukebox.votes:
        db.session.delete(vote)

    for relation in current_jukebox.relations:
        db.session.delete(relation)

    for guest in current_jukebox.guests:
        db.session.delete(guest)

    for admin in current_jukebox.admin:
        db.session.delete(admin)

    db.session.delete(current_jukebox)
    db.session.commit()

    session.clear()

    return redirect(url_for('shows_goodbye'))


@app.route("/goodbye", methods=['GET'])
def shows_goodbye():
    """Says goodbye to the user."""

    return render_template('goodbye.html')


################################################################################
### (5) Running the app


if __name__ == "__main__":

    # Output in console and needs to be True to invoke DebugToolbarExtension
    app.debug = True

    # Flask debug toolbar "secret key"
    app.secret_key = "MEOW"

    # SQLAlchemy track modifications setting explicitly
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Use debug toolbar
    DebugToolbarExtension(app)

    # Connect to database and run the app
    connect_to_db(app)
    # app.run()

    container = WSGIContainer(app)
    server = Application([
        (r'/websocket/', WebSocket),
        (r'.*', FallbackHandler, dict(fallback=container))
    ])
    server.listen(5000)
    IOLoop.instance().start()

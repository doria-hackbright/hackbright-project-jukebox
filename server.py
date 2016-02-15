"""Office Jukebox: Server"""

# Standard Python Libraries
from datetime import datetime
import os
import threading

# Flask
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

# Other External Libraries
import spotify
import requests

# Models (and Bottles)
from model import *


################################################################################
### (1) Setting up Flask app

app = Flask(__name__)


################################################################################
### (2) Supporting functions


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
### (3) App routes

@app.route("/")
def homepage():
    """Renders the homepage where users can create a jukebox."""

    return render_template('homepage.html')


@app.route("/jukebox", methods=['POST'])
def new_jukebox():
    """Renders the full jukebox in admin view."""

    new_jukebox = Jukebox.create()
    new_jukebox_id = new_jukebox.jukebox_id
    session['jukebox_id'] = new_jukebox_id

    new_user = JukeboxAdmin.create(jukebox_id=new_jukebox_id)
    session['user_id'] = new_user.admin_id

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


@app.route("/guest", methods=['POST'])
def new_guest():
    """Creates a new guest."""

    jukebox_id = request.form.get('jukebox_id')
    print jukebox_id
    new_user = JukeboxGuest.create(jukebox_id)
    print new_user
    print new_user.guest_id
    session['user_id'] = new_user.guest_id
    print session['user_id']

    print "YAY, NEW GUEST!"

    return redirect(url_for('jukebox_public', jukebox_id=jukebox_id))


@app.route("/songs", methods=['GET'])
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

    # Create a new song to add into the database
    new_song = Song.create(song_uri)

    return song_name + " has been added."


@app.route("/jukebox/<jukebox_id>/delete", methods=['POST'])
def delete_jukebox(jukebox_id):
    """Deletes a jukebox and all of its admin, guests, votes, and songs."""

    current_jukebox = Jukebox.query.get(jukebox_id)

    for admin in current_jukebox.admin:
        db.session.delete(admin)

    for guest in current_jukebox.guests:
        db.session.delete(guest)

    for song in current_jukebox.songs:
        db.session.delete(song)

    for vote in current_jukebox.votes:
        db.session.delete(vote)

    db.session.delete(current_jukebox)
    db.session.commit()

    return redirect(url_for('shows_goodbye'))


@app.route("/goodbye", methods=['GET'])
def shows_goodbye():
    """Says goodbye to the user."""

    return render_template('goodbye.html')


################################################################################
### (4) Running the app

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
    app.run()

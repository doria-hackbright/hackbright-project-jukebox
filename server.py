"""Office Jukebox: Server"""

# Standard Python Libraries
import os

# Flask
from flask import Flask, render_template, redirect, request, session, url_for, jsonify, Response

# Tornado
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler
from tornado.ioloop import IOLoop

# Other External Libraries
import requests

# Models (and Bottles)
from model import *

# Sockets and Jukebox Elements
from jukebox_sockets import *
from jukebox_elements import *


################################################################################
### (1) Setting up Flask app

app = Flask(__name__)


################################################################################
### (2) App routes


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


@app.route("/jukebox", methods=['POST'])
def new_jukebox():
    """Creates new jukebox and admin, adds to db, renders admin view."""

    new_jukebox = Jukebox.create()
    new_jukebox_id = new_jukebox.jukebox_id
    session['jukebox_id'] = new_jukebox_id

    new_user = JukeboxAdmin.create(jukebox_id=new_jukebox_id)
    session['admin_id'] = new_user.admin_id

    return redirect(url_for('jukebox_private', jukebox_id=new_jukebox_id))


@app.route("/guest", methods=['POST'])
def new_guest():
    """Creates a new guest."""

    jukebox_id = request.form.get('jukebox_id')
    print jukebox_id

    if not session.get('guest_id'):
        print session.get('guest_id')

        new_user = JukeboxGuest.create(jukebox_id=jukebox_id)
        session['guest_id'] = new_user.guest_id
        session['jukebox_id'] = jukebox_id

    return redirect(url_for('jukebox_public', jukebox_id=jukebox_id))


@app.route("/jukebox/<jukebox_id>/delete", methods=['POST'])
def delete_jukebox(jukebox_id):
    """Deletes a jukebox and all of its admin, guests, votes, and songs."""

    current_jukebox = Jukebox.query.get(jukebox_id)

    for relation in current_jukebox.relations:
        for vote in relation.votes:
            db.session.delete(vote)
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


@app.route("/jukebox_id", methods=['GET'])
def jukebox_id():
    """Returns jukebox_id."""

    return jsonify({"jukebox_id": session.get('jukebox_id')})


@app.route("/guest_id", methods=['GET'])
def guest_id():
    """Returns guest_id and jukebox_id they belong to."""

    return jsonify({"jukebox_id": session.get('jukebox_id'),
                    "guest_id": session.get('guest_id')})


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
                     "song_user_id": relation.song_user_id,
                     "jukebox_id": session['jukebox_id'],
                     "guest_id": session.get('guest_id'),
                     "new_song": True}

    return jsonify(response_dict)


@app.route("/play_song")
def play_song():
    def generate_raw_data():
        """Generate raw wave data."""

        raw_data_file = open('123.wav', 'rb')
        raw_data_contents = raw_data_file.read()
        raw_data_file.close()
        yield raw_data_contents

    return Response(generate_raw_data())


@app.route("/jukebox/<jukebox_id>/vote", methods=["POST"])
def create_vote(jukebox_id):
    """Guests can send votes for songs."""

    vote_value = request.form.get('vote-value')
    song_user_id = request.form.get('song-user-relation')
    guest_id = request.form.get('guest-id')
    voter_id = request.form.get('voter-id')

    print vote_value, song_user_id, guest_id, voter_id

    # Check that the song was not added by the user
    if voter_id == guest_id:
        return jsonify({"message": "Hey, you can't vote for a song you added!",
                        "jukebox_id": jukebox_id})

    # Check that the song was not already voted on by the user
    voter_vote_list = Vote.query.filter(Vote.voter_id == int(voter_id)).all()

    for v in voter_vote_list:
        if v.song_user_id == int(song_user_id):
            return jsonify({"message": "Sorry, you already voted on this song!",
                            "jukebox_id": jukebox_id})

    new_vote = Vote.create(song_user_id=int(song_user_id),
                           voter_id=int(voter_id),
                           vote_value=int(vote_value))

    response_dict = {"message": "Okay, you voted for this song!",
                     "vote_value": vote_value,
                     "song_user_id": song_user_id,
                     "jukebox_id": jukebox_id,
                     "vote_update": True}

    return jsonify(response_dict)


################################################################################
### (3) Running the app

container = WSGIContainer(app)
tornado_app = Application([
    (r'/playlist_socket/', PlaylistSocket),
    (r'/player_socket/', PlayerSocket),
    (r'.*', FallbackHandler, dict(fallback=container))
])

if __name__ == "__main__":

    # Flask app debug console output
    app.debug = True

    # Flask session secret key
    app.secret_key = os.environ['FLASK_SECRET_KEY']

    # SQLAlchemy track modifications setting explicitly
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Connect to database and run the app
    connect_to_db(app)
    tornado_app.listen(5000)
    IOLoop.instance().start()

"""Office Jukebox: Server"""

# Standard Python Libraries
from datetime import datetime

# Flask
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

# Other External Libraries
import spotify

# Models (and Bottles)
from model import *


################################################################################
### (1) Setting up Flask app

app = Flask(__name__)


################################################################################
### (2) Supporting functions


################################################################################
### (3) App routes

@app.route("/")
def homepage():
    """Renders the homepage where users can create a jukebox."""

    return render_template('homepage.html')


@app.route("/jukebox", methods=['POST'])
def jukebox_admin():
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

    return render_template('jukebox_admin.html')


@app.route("/guest", methods=['POST'])
def new_guest():
    """Creates a new guest."""

    jukebox_id = request.form.get('jukebox_id')
    print jukebox_id
    new_user = PlaylistGuest.create(jukebox_id)
    print new_user
    session['user_id'] = new_user.guest_id

    print "YAY, NEW GUEST!"

    return 200

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

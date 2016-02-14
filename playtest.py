################################################################################
### Spotify Playtest Script

# This file is a test for making API calls to Spotify
# The URI is for the song "Softly" by Kye Kye
# spotify:track:230yvxJzwVW8tH4Wb6gcvj
# Alternative URI spotify:track:5GCrBPWKpgH4H3bLLnvWm7

import spotify
import threading
import os

session = spotify.Session()

# The login() method is asynchronous, so we must ask the session to process the
# event until we are logged in properly.

# This can be done using an event loop provided by Pyspotify.

# First set up an event for logged_in
logged_in_event = threading.Event()


def connection_state_listener(session):
    """A function that sets the logged in thread event to true.

    The thread signals the event and other threads wait for it."""

    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in_event.set()
        print "I'M LOGGED IN"


# Start the Pyspotify event loop
loop = spotify.EventLoop(session)
loop.start()

# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED,
           connection_state_listener)

# Set environment variables for Spotify login
session.login(os.environ['SPOTIFY_UN'], os.environ['SPOTIFY_PW'])

# Blocks the thread until the event becomes True, which will be triggered by
# function connection_state_listener, attached to the session event listener
logged_in_event.wait()

# from pdb import set_trace
# set_trace()

# We can use the same event loop to set up our track playing, same logic

# First we set up an event for end_of_track
end_of_track = threading.Event()


def end_of_track_signal(session):
    """Success handler to set the end_of_track event"""

    end_of_track.set()
    print "THE TRACK IS DONE PLAYING"


# Register event listener for the end of the track
session.on(spotify.SessionEvent.END_OF_TRACK, end_of_track_signal)

# Connect an audio sink
audio = spotify.PortAudioSink(session)

# Play a track
track_uri = "spotify:track:5GCrBPWKpgH4H3bLLnvWm7"
track = session.get_track(track_uri).load()
session.player.load(track)
session.player.play()

while not end_of_track.wait(0.1):
    pass

session.logout()

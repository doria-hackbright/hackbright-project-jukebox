"""Office Jukebox: Spotify Player"""

# Standard Python Libraries
from collections import deque
import threading
import os

# Other External Libraries
import spotify

# Models (and Bottles)
from model import *


################################################################################
### (1) Spotify Player and Playlist Setup

class Playlist(object):
    """Set up the playlist class."""

    def __init__(self):
        """Set a playlist when instantiated."""

        self._playlist = deque()

    def load_playlist(self, jukebox_id):
        """Loads the current playlist for the jukebox based on votes."""

        # Empty out the deque
        self._playlist = deque()

        # Query for all the song/user relationships for the playlist so far
        relation_list = (SongUserRelationship.query
                                             .filter_by(jukebox_id=jukebox_id)
                                             .order_by('timestamp')
                                             .all())

        # Create a dictionary for all the votes for each song
        # Use a tuple that contains the vote value and the negative version
        # of the song_user_id, which will ensure that when we get the sorted
        # version of the dictionary, it will be ordered in descending order
        # by votes and ascending order by song_user_id
        relation_dict = dict()

        for r in relation_list:
            if r.votes:
                relation_dict.setdefault(r, (sum(v.vote_value for v in r.votes),
                                             -r.song_user_id))
            else:
                relation_dict.setdefault(r, (0, -r.song_user_id))

        # Using the dictionary, construct the playlist deque based on
        # the tuple (# of votes, id)

        for r in sorted(relation_dict,
                        key=relation_dict.get,
                        reverse=True):
            self._playlist.append((r, relation_dict.get(r, 0)))


class SpotifyPlayer(object):
    """A player for Spotify tracks."""

    def __repr__(self):
        """Set class representation."""

        return "<Class: SpotifyPlayer>"

    def _start_session(self):
        """Starts a Spotify session attribute."""

        # TODO: should check if a session is already running
        # or end all other active sessions... hmmm.
        self._session = spotify.Session()

    def _logged_in_listener(self, session):
        """Event listener that sets logged in thread event to true.

        The thread signals the event and other threads wait for it."""

        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self._logged_in.set()
            print("###########################################")
            print("LOGGED IN: %r" % (session.connection.state))
            print("###########################################")

    def _login(self):
        """Logs into Spotify to access playing music.

        A session attribute needs to be initiated first."""

        # TODO: check that a session attribute has been initiated before setting login listeners
        # Set up event for "logged in" and a listener for the connection state
        self._logged_in = threading.Event()

        # Set up Pyspotify event loop
        _loop = spotify.EventLoop(self._session)
        _loop.start()

        # Register event listener
        self._session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED,
                         self._logged_in_listener)

        # Login using environment variables
        self._session.login(os.environ['SPOTIFY_UN'], os.environ['SPOTIFY_PW'])

        # Blocks the thread until the event becomes True, which will be triggered
        # by _logged_in_listener (success handler), attached to the session
        # event listener
        self._logged_in.wait()

    def _play_track(self, spotify_uri):
        """Play a track loaded in session."""

        # set up an event for the end of track
        end_of_track = threading.Event()

        def end_of_track_signal(session):
            """Success handler to set the end_of_track event."""

            end_of_track.set()
            print "THE TRACK IS DONE PLAYING"

        # Register event listener for the end of the track
        self._session.on(spotify.SessionEvent.END_OF_TRACK, end_of_track_signal)

        spotify.PortAudioSink(self._session)
        track = self._session.get_track(spotify_uri).load()
        self._session.player.load(track)
        self._session.player.play()

        # while not end_of_track.wait(0.1):
        #     pass

    def _pause_track(self):
        """Pause the currently loaded track."""

        self._session.player.pause()

    def _unload(self):
        """Stops the currently playing track."""

        self._session.player.unload()

    def _prefetch(self, track):
        """Prefetches a track for playback.

        Libspotify will download and cache a track before playing it."""

        self._session.player.prefetch(track)

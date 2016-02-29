"""Office Jukebox: Spotify Player"""

# Standard Python Libraries
import threading

# Other External Libraries
import spotify

# Models (and Bottles)
from model import *


################################################################################
### (2) Spotify Player Setup

class SpotifyPlayer(object):
    """A player for Spotify tracks."""

    def __init__(self):
        """Set a Spotify session when a class is initialized."""

        self._session = spotify.Session()

    def __repr__(self):
        """Set class representation."""

        return "<Class: SpotifyPlayer>"

    def _login(self):
        """Logs into Spotify to access playing music."""

        # Set up event for "logged in" and a listener for the connection state
        _logged_in = threading.Event()

        def _logged_in_listener(self):
            """Event listener that sets logged in thread event to true.

            The thread signals the event and other threads wait for it."""

            if self._session.connection.state is spotify.ConnectionState.LOGGED_IN:
                _logged_in.set()
                print("###########################################")
                print("LOGGED IN: %r" % (session.connection.state))
                print("###########################################")

        # Set up Pyspotify event loop
        _loop = spotify.EventLoop(self._session)
        _loop.start()

        # Register event listener
        self._session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED,
                         _logged_in_listener)

        # Login using environment variables
        session.login(os.environ['SPOTIFY_UN'], os.environ['SPOTIFY_PW'])

        # Blocks the thread until the event becomes True, which will be triggered
        # by _logged_in_listener (success handler), attached to the session
        # event listener
        _logged_in.wait()

    def _set_audio(self):
        """Sets up Port Audio Sink for playing audio."""

        self._audio = spotify.PortAudioSink(self._session)

    def _get_track(self, spotify_uri):
        """Loads session with Spotify track based on given URI."""

        return self._session.get_track(spotify_uri).load()

    def _load_player(self, track):
        """Loads session player with track."""

        self._session.player.load(track)

    def _play_track(self):
        """Play a track loaded in session."""

        self._session.player.play()

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

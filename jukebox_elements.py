"""Office Jukebox: Spotify Player"""

# Standard Python Libraries
from collections import deque
import wave
import threading
import os

# Other External Libraries
import spotify

# Models (and Bottles)
from model import *


################################################################################
### (1) Spotify Player and Playlist Setup


class MyPortAudio(spotify.PortAudioSink):
    """Trying to get audio port to write into a buffer."""

    def __init__(self, session):
        super(MyPortAudio, self).__init__(session)
        self._buffer = wave.open("123.wav", "wb")
        self._buffer.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))

    def _on_music_delivery(self, session, audio_format, frames, num_frames):
        # super(MyPortAudio, self)._on_music_delivery(session, audio_format, frames, num_frames)
        assert (
            audio_format.sample_type == spotify.SampleType.INT16_NATIVE_ENDIAN)

        self._buffer.writeframes(frames)
        return num_frames

    def _reset_buffer(self):
        self._buffer = wave.open("123.wav", "wb")
        self._buffer.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))

    def _close(self):
        super(MyPortAudio, self)._close()
        self._buffer.close()


class Playlist(object):
    """Set up the playlist class."""

    def __init__(self):
        """Set a playlist when instantiated."""

        self._playlist = deque()

    def load_playlist(self, jukebox_id):
        """Loads the current playlist for the jukebox based on votes."""

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
                relation_dict.setdefault(r, (r.total_vote_value(),
                                             -r.song_user_id))
            else:
                relation_dict.setdefault(r, (0, -r.song_user_id))

        # Using the dictionary, construct the playlist deque based on
        # the tuple (# of votes, id)

        sorted_relationships = sorted(relation_dict,
                                      key=relation_dict.get,
                                      reverse=True)

        self._playlist = deque(sorted_relationships)

    def delete_song_from_playlist(self, jukebox_id):
        """Deletes a song from the database when it is played."""

        self.load_playlist(jukebox_id)

        if self._playlist:
            current_song = self._playlist[0].song_user_id
            relation = SongUserRelationship.query.get(current_song)
            for vote in relation.votes:
                db.session.delete(vote)
            db.session.delete(relation)
            db.session.commit()


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

    def _set_audio_sink(self):
        """Sets audio sink for device."""

        # Patch the Spotify Port Audio Sink with this current Port Audio Sink
        spotify.PortAudioSink = MyPortAudio
        self._audio = spotify.PortAudioSink(self._session)

        print("###########################################")
        print("Audio sink set")
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

        # Toggle Audio Sink to clear buffer
        self._audio._reset_buffer()

        # Check if player state is loaded
        if self._session.player.state == "unloaded":

            # set up an event for the end of track
            end_of_track = threading.Event()

            def end_of_track_signal(session):
                """Success handler to set the end_of_track event."""

                end_of_track.set()
                print "THE TRACK IS DONE PLAYING"

            # Register event listener for the end of the track
            self._session.on(spotify.SessionEvent.END_OF_TRACK, end_of_track_signal)

            track = self._session.get_track(spotify_uri).load()
            self._session.player.load(track)

        self._session.player.play()

        # while not end_of_track.wait(0.1):
        #     pass

    def _pause_track(self):
        """Pause the currently loaded track."""

        # Check if the player is currently playing
        if self._session.player.state == "playing":
            self._session.player.pause()

    def _unload(self):
        """Stops the currently playing track."""

        # Check if the player is currently loaded
        if self._session.player.state == "loaded" or self._session.player.state == "paused":
            self._session.player.unload()

        if self._session.player.state == "playing":
            self._session.player.pause()
            self._session.player.unload()

    def _prefetch(self, track):
        """Prefetches a track for playback.

        Libspotify will download and cache a track before playing it."""

        self._session.player.prefetch(track)

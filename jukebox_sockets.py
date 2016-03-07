"""Office Jukebox: WebSockets"""

# Standard Python Libraries
import json

# Tornado
from tornado.websocket import WebSocketHandler

# Other External Libraries
import spotify

# Models (and Bottles)
from model import *

# Controls
from jukebox_elements import *


################################################################################
### (1) WebSocket Setup


# Global dict to keep track of playlists by jukebox
JUKEBOX_ID_TO_PLAYLIST = dict()
JUKEBOX_SESSIONS = dict()


class PlaylistSocket(WebSocketHandler):
    """Set up WebSocket handlers for playlist information."""

    # Dictionary of connections based on jukebox
    connections = dict()

    def _add_connection(self, jukebox_id):
        """Add a new connection to the connections dict."""

        self.connections.setdefault(jukebox_id, set()).add(self)
        return self.connections

    def _current_playlist(self, jukebox_id):
        """Add a new playlist to global playlist dict."""

        current_playlist = JUKEBOX_ID_TO_PLAYLIST.setdefault(jukebox_id, Playlist())
        current_playlist.load_playlist(jukebox_id)

        return current_playlist

    def render_new_playlist(self, current_playlist):
        """Renders the current state of the playlist, ordered by votes."""

        # TODO: WRAP playlist_row INTO A FUNCTION
        i = 0
        for r in current_playlist:
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": r.total_vote_value(),
                            "order": i,
                            "first_load": True}
            self.write_message(playlist_row)

    def vote_playlist_update(self, jukebox_id, current_playlist):
        """Re-renders the current playlist based on new votes."""

        # TODO: USE ENUMERATE
        i = 0
        for r in current_playlist:
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": r.total_vote_value(),
                            "vote_update": True,
                            "order": i}
            for c in self.connections[jukebox_id]:
                c.write_message(playlist_row)
            i += 1

    def new_song_playlist_update(self, jukebox_id, current_playlist):
        """Re-renders the current playlist based on new votes."""

        i = 0
        for r in current_playlist:
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": r.total_vote_value(),
                            "new_song": True,
                            "order": i}
            for c in self.connections[jukebox_id]:
                c.write_message(playlist_row)
            i += 1

    def play_playlist_update(self, jukebox_id, current_playlist):
        """Re-renders the current playlist based on new votes."""

        i = 0
        for r in current_playlist:
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": r.total_vote_value(),
                            "play": True,
                            "order": i}
            for c in self.connections[jukebox_id]:
                c.write_message(playlist_row)
            i += 1

    def open(self):
        """Runs when WebSocket is open."""

        print "Socket connected!"

    def on_message(self, message):
        """Runs when a message is recieved from the WebSocket."""

        print message

        jukebox_id = json.loads(message).get('jukebox_id')
        print("####################################")
        print(jukebox_id)
        print("####################################")

        # If this is the first time loading a playlist
        if json.loads(message).get('first_load'):
            self._add_connection(jukebox_id)

            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self.render_new_playlist(current_playlist)

        if json.loads(message).get('vote_update'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self.vote_playlist_update(jukebox_id, current_playlist)

        if json.loads(message).get('new_song'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self.new_song_playlist_update(jukebox_id, current_playlist)

        if json.loads(message).get('play'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if len(current_playlist) > 0:
                current_playlist = self._current_playlist(jukebox_id)._playlist
                self.play_playlist_update(jukebox_id, current_playlist)

        if json.loads(message).get('empty_playlist'):
            for c in self.connections[jukebox_id]:
                c.write_message(message)

    def on_close(self):
        """Runs when a socket is closed."""

        print "####################################"
        print "Code:", self.close_code, "Reason:", self.close_reason
        print "Playlist socket disconnected!"
        print "####################################"


class PlayerSocket(WebSocketHandler):
    """Set up WebSocket handlers for music player."""

    # Dictionary of jukebox connections
    connections = dict()

    def _add_connection(self, jukebox_id):
        """Add a new connection to the connections dict."""

        self.connections.setdefault(jukebox_id, set()).add(self)
        return self.connections

    def _add_session(self, jukebox_id):
        """Add a new session to the session dict."""

        JUKEBOX_SESSIONS.setdefault(jukebox_id, SpotifyPlayer())

    def _current_playlist(self, jukebox_id):
        """Add a new playlist to global playlist dict."""

        current_playlist = JUKEBOX_ID_TO_PLAYLIST.setdefault(jukebox_id, Playlist())
        current_playlist.load_playlist(jukebox_id)

        return current_playlist

    def open(self):
        """Runs when WebSocket is open."""

        print "####################################"
        print "Player socket connectd!"
        print "####################################"

    def on_message(self, message):
        """Runs when a message is recieved from the WebSocket."""

        print message

        jukebox_id = json.loads(message).get('jukebox_id')

        print "####################################"
        print jukebox_id
        print "####################################"

        # need to add a different spotify session for each jukebox
        if json.loads(message).get('first_load'):
            self._add_session(jukebox_id)
            self._add_connection(jukebox_id)
            jukebox_player = JUKEBOX_SESSIONS.get(jukebox_id)

            # start a spotify session and login
            jukebox_player._start_session()
            jukebox_player._login()
            jukebox_player._set_audio_sink()

        jukebox_player = JUKEBOX_SESSIONS.get(jukebox_id)

        # check the message type:
            # play, pause, skip

        # skip: skips then plays the next song
        if json.loads(message).get('skip'):
            # unload current song
            jukebox_player._pause_track()
            jukebox_player._unload()

        # play
        if json.loads(message).get('play'):

            # get the current playlist
            current_playlist = self._current_playlist(jukebox_id)._playlist

            # if the current playlist has stuff in it
            if len(current_playlist) > 0:

                # pop off the URI for the first song
                current_song = current_playlist.popleft()
                song_uri = current_song.song.spotify_uri
                jukebox_player._play_track(song_uri)

            # delete the song
            current_playlist = self._current_playlist(jukebox_id)
            current_playlist.delete_song_from_playlist(jukebox_id)

            # reload current playlist
            current_playlist = self._current_playlist(jukebox_id)._playlist

            for c in self.connections[jukebox_id]:
                c.write_message(message)

            if not current_playlist:
                empty_playlist = '{"empty_playlist" : "true", ' + '"jukebox_id" : ' + '"' + jukebox_id + '"' + '}'
                for c in self.connections[jukebox_id]:
                    c.write_message(empty_playlist)

        # pause
        if json.loads(message).get('pause'):
            # pause the player
            jukebox_player._pause_track()

    def on_close(self):
        """Runs when a socket is closed."""

        print "####################################"
        print "Code:", self.close_code, "Reason:", self.close_reason
        print "Player socket disconnected!"
        print "####################################"

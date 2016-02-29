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
PLAYLIST_DICT = dict()


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

        current_playlist = PLAYLIST_DICT.setdefault(jukebox_id, Playlist())
        current_playlist.load_playlist(jukebox_id)

        return current_playlist

    def _render_new_playlist(self, current_playlist):
        """Renders the current state of the playlist, ordered by votes."""

        # Need to add secondary sort condition using lambda by r.song_user_id?
        # How will that interact with reverse?
        # Can just set one variable to negative in the lambda... huh...
        for r in current_playlist:
            playlist_row = {"song_name": r[0].song.song_name,
                            "song_artist": r[0].song.song_artist,
                            "song_album": r[0].song.song_album,
                            "song_user_id": r[0].song_user_id,
                            "guest_id": r[0].user_id,
                            "song_votes": r[1][0]}
            self.write_message(playlist_row)

    def _vote_playlist_update(self, jukebox_id, current_playlist):
        """Re-renders the current playlist based on new votes."""

        i = 0
        for r in current_playlist:
            playlist_row = {"song_name": r[0].song.song_name,
                            "song_artist": r[0].song.song_artist,
                            "song_album": r[0].song.song_album,
                            "song_user_id": r[0].song_user_id,
                            "guest_id": r[0].user_id,
                            "song_votes": r[1][0],
                            "vote_update": True,
                            "order": i}
            for c in self.connections[jukebox_id]:
                c.write_message(playlist_row)
            i += 1

    def open(self):
        """Runs when WebSocket is open."""

        print "Socket connected!"

    def on_message(self, message):
        """Runs when a message is recieved from the WebSocket."""

        jukebox_id = json.loads(message).get('jukebox_id')
        print "####################################"
        print jukebox_id
        print "####################################"

        # If this is the first time loading a playlist
        if json.loads(message).get('first_load'):
            self._add_connection(jukebox_id)

            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self._render_new_playlist(current_playlist)

        if json.loads(message).get('vote_value'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self._vote_playlist_update(jukebox_id, current_playlist)

        # Write the update to all connections
        for c in self.connections[jukebox_id]:
            c.write_message(message)

    def on_close(self):
        """Runs when a socket is closed."""

        print "####################################"
        print "Code:", self.close_code, "Reason:", self.close_reason
        print "Socket disconnected!"
        print "####################################"


class PlayerSocket(WebSocketHandler):
    """Set up WebSocket handlers for music player."""

    def open(self):
        """Runs when WebSocket is open."""

        self._spotify_player = SpotifyPlayer()
        print self._spotify_player
        print "Player connectd!"

    def on_message(self):
        """Runs when a message is recieved from the WebSocket."""

        # check the message type:
            # play, pause, skip

        # play
            # query the current playlist
            # get URI of first song
            # load that song
            # play that song

        # pause
            # pause the player

        # skip
            # unload current song
            # query the current playlist
            # get URI of the next song
            # load that song
            # play that song

    def on_close(self):
        """Runs when a socket is closed."""

        print "####################################"
        print "Code:", self.close_code, "Reason:", self.close_reason
        print "Socket disconnected!"
        print "####################################"

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
from jukebox_player import *


################################################################################
### (1) WebSocket Setup


class PlaylistSocket(WebSocketHandler):
    """Set up WebSocket handlers for playlist information."""

    # Dictionary of connections based on jukebox
    connections = dict()

    def _add_connection(self, jukebox_id):
        """Add a new connection to the connections dict."""

        self.connections.setdefault(jukebox_id, set()).add(self)
        return self.connections

    def _load_current_playlist(self, jukebox_id):
        """Returns current playlist for a jukebox based on votes."""

        # Query for all the song/user relationships for the playlist so far
        relation_list = (SongUserRelationship.query
                                             .filter_by(jukebox_id=jukebox_id)
                                             .order_by('timestamp')
                                             .all())

        # Create a dictionary for all the votes for each song
        relation_dict = dict()

        for r in relation_list:
            if r.votes:
                relation_dict.setdefault(r, sum(v.vote_value for v in r.votes))
            else:
                relation_dict.setdefault(r, 0)

        return relation_dict

    def _render_new_playlist(self, current_playlist):
        """Renders the current state of the playlist, ordered by votes."""

        # Need to add secondary sort condition using lambda by r.song_user_id?
        # How will that interact with reverse?
        # Can just set one variable to negative in the lambda... huh...
        for r in sorted(current_playlist,
                        key=current_playlist.get,
                        reverse=True):
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": current_playlist.get(r, 0)}
            self.write_message(playlist_row)

    def _vote_playlist_update(self, jukebox_id, current_playlist):
        """Re-renders the current playlist based on new votes."""

        i = 0
        for r in sorted(current_playlist,
                        key=current_playlist.get,
                        reverse=True):
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": current_playlist.get(r, 0),
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

            current_playlist = self._load_current_playlist(jukebox_id)

            if current_playlist:
                self._render_new_playlist(current_playlist)

        if json.loads(message).get('vote_value'):
            current_playlist = self._load_current_playlist(jukebox_id)

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

        #

    def on_close(self):
        """Runs when a socket is closed."""

        print "####################################"
        print "Code:", self.close_code, "Reason:", self.close_reason
        print "Socket disconnected!"
        print "####################################"

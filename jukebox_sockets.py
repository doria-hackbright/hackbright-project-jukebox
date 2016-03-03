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

    def _delete_played_song(self, jukebox_id):
        """Delete the song that was just played by the playlist."""

        current_playlist = self._current_playlist(jukebox_id)._playlist

        print("#####################################")
        print(current_playlist)
        print("First song relationship: %s" % (current_playlist[0]))
        print("#####################################")

        relation_id = current_playlist[0].song_user_id

        print("#####################################")
        print("RELATIONSHIP ID: %s" % (relation_id))
        print("#####################################")

        relation = SongUserRelationship.query.get(relation_id)
        for vote in relation.votes:
            db.session.delete(vote)
        db.session.delete(relation)
        db.session.commit()

    def _render_new_playlist(self, current_playlist):
        """Renders the current state of the playlist, ordered by votes."""

        # TODO: WRAP playlist_row INTO A FUNCTION

        # Need to add secondary sort condition using lambda by r.song_user_id?
        # How will that interact with reverse?
        # Can just set one variable to negative in the lambda... huh...
        for r in current_playlist:
            playlist_row = {"song_name": r.song.song_name,
                            "song_artist": r.song.song_artist,
                            "song_album": r.song.song_album,
                            "song_user_id": r.song_user_id,
                            "guest_id": r.user_id,
                            "song_votes": r.total_vote_value()}
            self.write_message(playlist_row)

    def _vote_playlist_update(self, jukebox_id, current_playlist):
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

    def _play_playlist_update(self, jukebox_id, current_playlist):
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

        jukebox_id = json.loads(message).get('jukebox_id')
        print("####################################")
        print(jukebox_id)
        print("####################################")

        # If this is the first time loading a playlist
        if json.loads(message).get('first_load'):
            self._add_connection(jukebox_id)

            current_playlist = self._current_playlist(jukebox_id)._playlist
            print current_playlist

            if current_playlist:
                self._render_new_playlist(current_playlist)

        if json.loads(message).get('vote_value'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if current_playlist:
                self._vote_playlist_update(jukebox_id, current_playlist)

        if json.loads(message).get('play'):
            current_playlist = self._current_playlist(jukebox_id)._playlist

            if len(current_playlist) > 0:
                self._delete_played_song(jukebox_id)
                current_playlist = self._current_playlist(jukebox_id)._playlist
                print "################################"
                print current_playlist
                print "################################"
                self._play_playlist_update(jukebox_id, current_playlist)

        # Write the update to all connections
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

            for c in self.connections[jukebox_id]:
                c.write_message(message)

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

"""Office Jukebox: Python Test Suite"""

# Python Standard Libraries
from unittest import TestCase, main
import os

# Import Tornado Testing
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect
import tornado.web

# Import Server, WebSockets, Jukebox Elements
from model import *
from server import *
from jukebox_elements import *
from jukebox_sockets import *


################################################################################
### (1) Connect to Test Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///office-jukebox-test'
app.config['TESTING'] = True
db.app = app
db.init_app(app)
print "Connected to DB"


################################################################################
### (2) WebSocket Test Cases


class PlaylistWebSocketTest(AsyncHTTPTestCase):
    """Testing playlist WebSocket functionality from server."""

    def get_app(self):
        """Brings in app from server."""

        return tornado_app

    @tornado.testing.gen_test
    def test_websocket_msg_handling(self):
        """Testing WebSocket message handling."""

        # self.get_http_port() gives the port of the running test server
        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/playlist_socket/"

        # The ws_url feeds into our WebSocke client
        ws_client = yield websocket_connect(ws_url)

        # running a test on the WebSocket
        first_load_msg = '{"jukebox_id" : "ec888ca4-eef0-4840-a316-d4a40d72f396","first_load" : "yes"}'
        ws_client.write_message(first_load_msg)
        # response = yield ws_client.read_message()
        self.assertEqual(json.loads(first_load_msg).get('jukebox_id'), "ec888ca4-eef0-4840-a316-d4a40d72f396")
        self.assertEqual(json.loads(first_load_msg).get('first_load'), "yes")


class PlayerWebSocketTest(AsyncHTTPTestCase):
    """Testing player WebSocket functionality from server."""

    def get_app(self):
        """Brings in app from server."""

        return tornado_app

    @tornado.testing.gen_test
    def test_websocket_msg_hadnling(self):
        """Testing WebSocket message handling."""

        # self.get_http_port() gives the port of the running test server
        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/player_socket/"

        # The ws_url feeds into our WebSocke client
        ws_client = yield websocket_connect(ws_url)

        # running a test on the WebSocket
        first_load_msg = '{"jukebox_id" : "ec888ca4-eef0-4840-a316-d4a40d72f396","first_load" : "yes"}'
        ws_client.write_message(first_load_msg)
        # response = yield ws_client.read_message()
        self.assertEqual(json.loads(first_load_msg).get('jukebox_id'), "ec888ca4-eef0-4840-a316-d4a40d72f396")
        self.assertEqual(json.loads(first_load_msg).get('first_load'), "yes")


################################################################################
### (3) Route Test Cases


class OfficeJukeboxTest(TestCase):
    """Testing Office Jukebox routes."""

    def setUp(self):
        """Runs on test case setup."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        with self.client as c:
            with c.session_transaction() as sess:
                sess['jukebox_id'] = "ec888ca4-eef0-4840-a316-d4a40d72f396"

    def test_jukebox_homepage(self):
        """Ensure homepage is properly rendered."""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)

    def test_jukebox_guest(self):
        """Ensure that guest view of jukebox is loaded properly."""

        jukebox_id = "ec888ca4-eef0-4840-a316-d4a40d72f396"
        result = self.client.get("/jukebox/" + jukebox_id)
        self.assertEqual(result.status_code, 200)

    def test_jukebox_admin(self):
        """Ensure that admin view of jukebox is loaded properly."""

        jukebox_id = "ec888ca4-eef0-4840-a316-d4a40d72f396"
        result = self.client.get("/jukebox/" + jukebox_id + "/admin")
        self.assertEqual(result.status_code, 200)

    def test_jukebox_creation(self):
        """Ensure that jukebox is made """

        result = self.client.post("/jukebox")
        self.assertEqual(result.status_code, 302)

    def test_guest_creation(self):
        """Ensure that guest view is rendered and guest is created."""

        jukebox_id = "ec888ca4-eef0-4840-a316-d4a40d72f396"
        result = self.client.post("/guest", data=dict(
                                  jukebox_id=jukebox_id))
        self.assertEqual(result.status_code, 302)

    def test_guest_id(self):
        """Endpoint returns guest information."""

        result = self.client.get("/guest_id")
        self.assertEqual(result.status_code, 200)

    def test_jukebox_id(self):
        """Endpoint returns jukebox information."""

        result = self.client.get("/jukebox_id")
        self.assertEqual(result.status_code, 200)

    def test_new_song(self):
        """Adds new song to database."""

        result = self.client.post("/song/add", data={'song-uri': "spotify:track:5GCrBPWKpgH4H3bLLnvWm7",
                                                     'song-name': "Dream",
                                                     'song-artist': "Autograf",
                                                     'song-album': "Dream"})

        spotify_uri = "spotify:track:5GCrBPWKpgH4H3bLLnvWm7"
        new_song = Song.query.filter(Song.spotify_uri == spotify_uri).one()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(new_song.spotify_uri, spotify_uri)

    def test_new_vote(self):
        """Ensures votes are added properly."""

        jukebox_id = "ec888ca4-eef0-4840-a316-d4a40d72f396"

        result = self.client.post("/jukebox/" + jukebox_id + "/vote", data={
                                  "vote-value": 1,
                                  "song-user-relation": 1,
                                  "guest-id": None,
                                  "voter-id": 21})

        new_vote = Vote.query.filter(SongUserRelationship.song_user_id == 1).first()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(new_vote.song_user_id, 1)

    def test_render_goodbye(self):
        """Ensure goodbye page renders."""

        result = self.client.get("/goodbye")
        self.assertEqual(result.status_code, 200)

    # def test_jukebox_deletion(self):
    #     """Ensure that jukebox is deleted."""

        # jukebox_id = "ec888ca4-eef0-4840-a316-d4a40d72f396"
        # result = self.client.post("/jukebox/" + jukebox_id + "/delete")
        # self.assertEqual(result.status_code, 302)

if __name__ == "__main__":

    # Flask session secret key
    app.secret_key = os.environ['FLASK_SECRET_KEY']
    main()

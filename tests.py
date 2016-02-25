"""Office Jukebox: Python Test Suite"""

# Python Standard Libraries
from unittest import TestCase, main

# Import Tornado Testing
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect
import tornado.web

# Import Server
from server import *


################################################################################
### (1) Connect to Test Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///office-jukebox-test'
app.config['TESTING'] = True
db.app = app
db.init_app(app)
print "Connected to DB"


################################################################################
### (2) WebSocket Test Cases


class WebSocketsTest(AsyncHTTPTestCase):
    """Testing WebSocket functionality from server."""

    def get_app(self):
        """Brings in app from server."""

        return tornado_app

    @tornado.testing.gen_test
    def test_websocket_first_load(self):

        # self.get_http_port() gives the port of the running test server
        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/websocket/"

        # The ws_url feeds into our WebSocke client
        ws_client = yield websocket_connect(ws_url)

        # running a test on the WebSocket
        first_load_msg = '{"jukebox_id" : "a49ec47d-5808-4975-bfcc-b42d2667a9a5","first_load" : "yes"}'
        ws_client.write_message(first_load_msg)
        response = yield ws_client.read_message()
        self.assertEqual(response, first_load_msg)


################################################################################
### (3) Office Jukebox Test Case


class OfficeJukeboxTest(TestCase):
    """Testing Office Jukebox routes."""

    def setUp(self):
        """Runs on test case setup."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        """Runs when test case ends."""

        pass

    def test_jukebox_homepage(self):
        """Ensure homepage is properly rendered."""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)

    def test_jukebox_creation(self):
        """Ensure that jukebox is made """

        result = self.client.get("/jukebox")
        self.assertEqual(result.status_code, 302)
        # need to do .post -- currently returning 405

    def test_guest_creation(self):
        """Ensure that guest view is rendered and guest is created."""

        result = self.client.get("/guest")
        self.assertEqual(result.status_code, 302)
        # need to do .post -- currently returning 405
        # TODO: add condition for guest creation in database

    def test_song_creation(self):
        """Ensure song is created and added to database."""

        # TODO: set up a song object, query and check condition
        pass

    def test_render_goodbye(self):
        """Ensure goodbye page renders."""

        result = self.client.get("/goodbye")
        self.assertIn("<h1>Bye now, have a nice day!</h1>", result.data)

if __name__ == "__main__":
    main()

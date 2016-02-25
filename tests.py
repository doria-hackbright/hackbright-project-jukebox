"""Office Jukebox: Python Test Suite"""

# Python Standard Libraries
from unittest import TestCase, main

# Import Tornado Testing
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect
from flask_sqlalchemy import SQLAlchemy
import tornado.web

# Import Server
from server import *


################################################################################
### (1) Mock Database Setup

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

        print "####################"
        # self.get_http_port() gives the port of the running test server
        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/websocket/"
        print ws_url

        # The ws_url feeds into our WebSocke client
        ws_client = yield websocket_connect(ws_url)

        # running a test on the WebSocket
        first_load_msg = '{"jukebox_id" : "a49ec47d-5808-4975-bfcc-b42d2667a9a5" ,"first_load" : "yes"}'
        ws_client.write_message(first_load_msg)
        response = yield ws_client.read_message()
        self.assertEqual(response, first_load_msg)


################################################################################
### (3) Office Jukebox Test Case


class OfficeJukeboxTest(TestCase):
    """Testing Office Jukebox routes."""
    pass

    def setUp(self):
        """Runs on test case setup."""

        # Mock database
        # Connect to mock database
        # Create all tables in mock db
        pass

    def tearDown(self):
        """Runs when test case ends."""

        # End mock database session
        # Drop all database tables in mock db
        pass

    def test_jukebox_creation(self):
        """Ensure that jukebox is made """
        pass

    def test_guest_creation(self):
        pass

    def test_admin_creation(self):
        pass

    def test_jukebox_id_get(self):
        pass

    def test_guest_id_get(self):
        pass

if __name__ == "__main__":
    main()

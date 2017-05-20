import unittest
import sys, os, io

from StringIO import StringIO 

from model import *
from server import *

# Test cases here
class NightOutTests(unittest.TestCase):
    """ Tests for Night Out app """
# Log in / log out and page viewability
    
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')
        db.create_all()

    def tearDown(self):
        """Runs at the end of every test."""

        db.session.close()
        db.drop_all()

    def test_homepage(self):
        """ Test that homepage has log in and new profile access"""
        result = self.client.get("/")
        self.assertIn("Night Out", result.data)
        self.assertIn("Create Account", result.data)
        self.assertNotIn("Profile", result.data) 

    def test_create_account(self):
        """ Test to check user creation completes successfully"""
        result = self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Maddows',
                                    'zip_code': '12345'},
                              follow_redirects=True)
        self.assertIn("now registered and logged in", result.data)
        self.assertIn("Create one now!", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Profile", result.data)
        self.assertNotIn("Log In", result.data)
        self.assertNotIn("Create Account", result.data)


class ServerTests(unittest.TestCase):
    """ Tests for server functionality """

# When plans added, user plans are correctly changed
# Invitee / User relationship

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')
        db.create_all()


if __name__ == "__main__":
    # Call testing function to run
    unittest.main()
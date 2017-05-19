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

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("Night Out", result.data)
        self.assertIn("")



class ServerTests(unittest.TestCase):
    """ Tests for server functionality """

# When plans added, user plans are correctly changed
# Invitee / User relationship


    def set up(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')
        db.create_all()


if __name__ == "__main__":
    # Call testing function to run
    unittest.main()
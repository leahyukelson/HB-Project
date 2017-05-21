import unittest
import sys, os, io

from StringIO import StringIO 

from model import *
from server import *

# Test cases here
class NewUserTests(unittest.TestCase):
    """ Tests for a new user in Night Out app """
    
    def setUp(self):
        """ Runs before every test """
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')
        db.create_all()

    def tearDown(self):
        """Runs at the end of every test """

        db.session.close()
        db.drop_all()

    def test_homepage(self):
        """ Test that homepage has log in and new profile access"""
        result = self.client.get("/")
        self.assertIn("Night Out", result.data)
        self.assertIn("Create Account", result.data)
        self.assertNotIn("Profile", result.data) 

    def test_create_account(self):
        """ Test that create account page is running with correct form """
        result = self.client.get('/create-account')
        self.assertIn("Create Account", result.data)
        self.assertIn("Submit", result.data)
        self.assertNotIn("Profile", result.data)

    def test_create_account(self):
        """ Test to check user creation completes successfully"""

        # Create account page correctly inputs new user and shows correct pages with logged in user
        result = self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray',
                                    'zip_code': '12345'},
                              follow_redirects=True)
        self.assertIn("now registered and logged in", result.data)
        self.assertIn("Create one now!", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Profile", result.data)
        self.assertNotIn("Log In", result.data)
        self.assertNotIn("Create Account", result.data)

        # Check user is correctly input in database
        new_user = User.query.filter_by(email='rachel@gmail.com').one()
        self.assertEqual(new_user.first_name, 'Rachel', 'User not created')
        self.assertNotEqual(new_user.password, '123', 'Password not hashed')

    def test_new_user_profile(self):
        """ Test to check no plans exist in new user profile, option to create one """
        self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray',
                                    'zip_code': '12345'},
                              follow_redirects=True)

        # User has profile with no plans, and a link to create plans
        result = self.client.get('/profile')
        self.assertIn("no plans", result.data)
        self.assertIn("/new-plan", result.data)


class NightPlanTests(unittest.TestCase):
    """ Tests for plan creation functionality """

# When plans added, user plans are correctly changed
# Invitee / User relationship

    def setUp(self):
        """ Runs before every test """
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')
        db.create_all()
        fill_example_data()

    def tearDown(self):
        """Runs at the end of every test """

        db.session.close()
        db.drop_all()

    def test_no_plan_profile(self):
        """ Test to check no plans exist in profile """

        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "rachel@gmail.com"

        # User has profile with no plans, and a link to create plans
        result = self.client.get('/profile')
        self.assertIn("no plans", result.data)
        self.assertIn("/new-plan", result.data)



if __name__ == "__main__":
    # Call testing function to run
    unittest.main()
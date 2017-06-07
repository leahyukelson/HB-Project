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

    def test_create_account_form(self):
        """ Test that create account page is running with correct form """
        result = self.client.get("/create-account")
        self.assertIn("Create Account", result.data)
        self.assertIn("submit", result.data)
        self.assertNotIn("Profile", result.data)

    def test_create_account(self):
        """ Test to check user creation completes successfully"""

        # Create account page correctly inputs new user and shows correct pages with logged in user
        result = self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray'},
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
                                    'last_name': 'Ray'},
                              follow_redirects=True)

        # User has profile with no plans, and a link to create plans
        result = self.client.get('/profile')
        self.assertIn("no plans", result.data)
        self.assertIn("/new-plan", result.data, 'No link to create new plan')

    def test_log_out(self):
        """ Test logging out of a newly created and logged in account """
        result = self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray'},
                              follow_redirects=True)

        # User clicks log out
        result = self.client.get('/logout', follow_redirects=True)
        self.assertIn("You are now logged out.", result.data, "Flash message not showing")
        self.assertIn("Log In", result.data, "Header not changed based on session")
        self.assertNotIn("Profile", result.data)

    def test_hashed_pw_login(self):
        """ Test logging in on a newly created account """
        self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray'},
                              follow_redirects=True)

        # User clicks log out
        self.client.get('/logout', follow_redirects=True)
        result = self.client.post("/check-login",
                                    data={'email': 'rachel@gmail.com',
                                          'password': '123'},
                                    follow_redirects=True)

        self.assertIn("You are now logged in!", result.data)
        self.assertIn("no plans", result.data)
        self.assertNotIn("Log In", result.data)

    def test_no_user_profile(self):
        """ Test that profile page redirects to log-in for a user not logged in """
        result = self.client.get('/profile', follow_redirects=True)
        self.assertIn("Log In", result.data, 'Page did not redirect')
        self.assertNotIn("Plans", result.data, 'Page did not redirect')


class NightPlanTests(unittest.TestCase):
    """ Tests for plan creation functionality """

# When plans added, user plans are correctly changed
# Invitee / User relationship

    def setUp(self):
        """ Runs before every test """
        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, 'postgresql:///test_plans')

        # To connect to Yelp JSON
        app.yelp_bearer_token = 'WllJxLDGOspRQnGbwsoqd9CFqeW8_LshxaRo1WZXWbTJ5-zCePPbNwW61x1NCJiX9-RIh7KMiP-3l7RxJtrqnczHAILypbXeduWluvi3zK0OTUorLHk_9E3TbIMTWXYx'

        db.create_all()
        fill_example_data()

    def tearDown(self):
        """Runs at the end of every test """

        db.session.close()
        db.drop_all()

    def test_create_same_account(self):
        """ Test to ensure same email cannot be registered more than once """

        # Create account with same email as user 1 from example data
        result = self.client.post("/create-account",
                              data={'email': 'rachel@gmail.com',
                                    'password': '123',
                                    'first_name': 'Rachel',
                                    'last_name': 'Ray'},
                              follow_redirects=True)

        self.assertIn("User email already exists", result.data, "Message did not flash")
        self.assertIn("Log In", result.data, "User was signed in")
        self.assertNotIn("now registered and logged in", result.data, "Allowed duplicate account creation")

    def test_log_in(self):
        """ Test to check redirect when logging into user from test database """
        result = self.client.post("/check-login",
                                data={'email': 'rachel@gmail.com',
                                      'password': 'word'},
                                follow_redirects=True)
        self.assertIn("Log Out", result.data)
        self.assertIn("Profile", result.data)
        self.assertNotIn("Log In", result.data)
        self.assertNotIn("Create Account", result.data)


    def test_wrong_password(self):
        """ Test to check redirect when logging on with incorrect password """
        result = self.client.post("/check-login",
                                data={'email': 'rachel@gmail.com',
                                      'password': 'oopsy'},
                                follow_redirects=True)
        self.assertIn("Wrong password!", result.data)
        self.assertIn("Log In", result.data)
        self.assertNotIn("You are now logged in!", result.data)

    def test_login_wrong_email(self):
        """ Test to check redirect when logging on with incorrect email """
        result = self.client.post("/check-login",
                                data={'email': 'oopsy@gmail.com',
                                      'password': 'oopsy'},
                                follow_redirects=True)

        self.assertIn("No user with that email", result.data)
        self.assertIn("Create Account", result.data)
        self.assertNotIn("You are now logged in!", result.data)

    def test_user_previously_invited(self):
        """ Test when a user signs up who is an invitee on a plan """
        # Create account with same email as user 1 from example data
        result = self.client.post("/create-account",
                              data={'email': 'bobby@gmail.com',
                                    'password': 'bbobb',
                                    'first_name': 'Bob',
                                    'last_name': 'Bobby'},
                              follow_redirects=True)

        # User should see previously invited plans on profile page
        self.assertIn("Night Out", result.data)
        self.assertIn("Poutinerie", result.data)
        self.assertNotIn("no plans", result.data)

    def test_no_plan_profile(self):
        """ Test to check no plans exist in profile """

        # Load in user1 (has no plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "rachel@gmail.com"

        # User has profile with no plans, and a link to create plans
        result = self.client.get('/profile')
        self.assertIn("no plans", result.data)
        self.assertIn("/new-plan", result.data)

    def test_with_plans_profile(self):
        """ Test plans show in profile when user has them """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/profile')
        self.assertIn("Plans", result.data)
        self.assertIn("Concert", result.data)
        self.assertIn("October 3, 2018", result.data)

    def test_event_creation_form(self):
        """ Test event create form """

        # Load in user1 (has no plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "rachel@gmail.com"

        result = self.client.get('/new-plan')
        self.assertIn('New Plan', result.data)
        self.assertIn('submit', result.data)

    def test_create_first_plan(self):
        """ Test creation of first plan """

        # Load in user1 (has no plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "rachel@gmail.com"

        # Test plan in form
        result = self.client.post("/new-plan",
                              data={'plan_name': "Mel's Birthday",
                                    'event_name': 'Drake Concert',
                                    'event_date': '2017-10-10',
                                    'event_time': '21:00',
                                    'location': 'Bill Graham Civic Center',
                                    'number': '99',
                                    'street' : 'Grove Street',
                                    'state' : 'CA',
                                    'city' : 'San Francisco',
                                    'zipcode' : '94102',
                                    'event_lat': '130',
                                    'event_long': '-50'},
                              follow_redirects=True)

        # Re-direct to choose-restaurant form
        self.assertIn("Meet at", result.data)
        self.assertIn("submit", result.data)
        self.assertNotIn("New Plan", result.data)

        # Check plan has been inputted into database
        new_plan = Plan.query.filter_by(event_name="Drake Concert").first()
        self.assertIn("Bill Graham Civic Center", new_plan.event_location, "Plan info not inputted in database")
        self.assertIn("2017-10-10 21:00:00", str(new_plan.event_time), "Datetime not inputted correctly")

        # Check userplan has been created to attribute plan to user
        userplan = UserPlan.query.filter_by(plan_id=new_plan.plan_id).first()
        self.assertIn("1", str(userplan.user_id), "User not attributed to new plan")

    def test_not_user_create_plan(self):
        """ Test creating a plan when no user in session """
        result = self.client.get('/new-plan', follow_redirects=True)
        self.assertIn("Log In", result.data)
        self.assertNotIn('New Plan', result.data)


    def test_create_no_name_plan(self):
        """ Test creation of plan with no name """

        # Load in user1 (has no plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "rachel@gmail.com"

        # Test plan in form
        result = self.client.post("/new-plan",
                              data={'plan_name': '',
                                    'event_name': 'The Weeknd Concert',
                                    'event_date': '2017-12-10',
                                    'event_time': '20:00',
                                    'location': 'Bill Graham Civic Center',
                                    'number': '99',
                                    'street' : 'Grove Street',
                                    'state' : 'CA',
                                    'city' : 'San Francisco',
                                    'zipcode' : '94102',
                                    'event_lat': '130',
                                    'event_long': '-50'},
                              follow_redirects=True)

        # Re-direct to choose-restaurant form
        self.assertIn("Meet at", result.data)
        self.assertIn("submit", result.data)
        self.assertNotIn("New Plan", result.data)

        # Check plan has been inputted into database
        new_plan = Plan.query.filter_by(event_name="The Weeknd Concert").first()
        self.assertIn("The Weeknd Concert", new_plan.plan_name, "Event name not inputted as plan name")

        # Check userplan has been created to attribute plan to user
        userplan = UserPlan.query.filter_by(plan_id=new_plan.plan_id).first()
        self.assertIn("1", str(userplan.user_id), "User not attributed to new plan")

    def test_customize_business(self):
        """ Test getting yelp json based on user's customizations """

        # Load in user1 (has no plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"


        # Path to choose restaurant for a plan already created
        result = self.client.post("/yelp.json",
                                data={'plan_id' : '1',
                                      'bar_or_rest': 'restaurants',
                                      'time_before': '1.5',
                                      'distance': '0.5'},
                                follow_redirects=True)

        self.assertIn("title", result.data, "Yelp call did not run")
        self.assertNotIn("Something went wrong.", result.data, "Yelp call failed explicitly")


    def test_edit_plan_form(self):
        """ Test editing plan functionality """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        # Path to choose to edit an already-existing plan
        result = self.client.get("/edit-plan/2")
        self.assertIn("Event name", result.data)
        self.assertIn("Location", result.data)

    def test_edit_plan(self):
        """ Test editing a plan's details, not address """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.post("/edit-plan/2",
                              data={'plan_name': "Mel's Birthday",
                                    'event_name': 'Drake Concert',
                                    'event_date': '2018-10-03',
                                    'event_time': '20:00',
                                    'location': 'Roman Theater',
                                    'number': '2001',
                                    'street' : 'Gayley Rd.',
                                    'state' : 'CA',
                                    'city' : 'Berkeley',
                                    'zipcode' : '94720',
                                    'event_lat': '130',
                                    'event_long': '-50'},
                              follow_redirects=True)

        # Check that page redirected to profile since location is unchanged
        self.assertIn("Plans", result.data)
        self.assertIn("Birthday", result.data)
        self.assertNotIn("Meet at", result.data, "Page re-directed to restaurant choosing")

        # Check plan was changed in database
        plan = Plan.query.get(2)
        self.assertIn("Drake Concert", plan.event_name)
        self.assertNotEqual("Night Out", plan.plan_name)


    def test_edit_address_plan(self):
        """ Test editing location of plan """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.post("/edit-plan/2",
                              data={'plan_name': "Night Out",
                                    'event_name': 'Concert',
                                    'event_date': '2018-10-03',
                                    'event_time': '20:00',
                                    'location': 'Bill Graham Civic Center',
                                    'number': '99',
                                    'street' : 'Grove Street',
                                    'state' : 'CA',
                                    'city' : 'San Francisco',
                                    'zipcode' : '94102',
                                    'event_lat': '130',
                                    'event_long': '-50'},
                              follow_redirects=True)

        # Page should re-direct to choose new business with new location at center
        self.assertIn("Meet at", result.data)
        self.assertIn("submit", result.data)
        self.assertNotIn("New Plan", result.data)

        # Check plan was changed in database
        plan = Plan.query.get(2)
        self.assertIn("Bill Graham Civic Center", plan.event_location)

    def test_edit_nonexistant_plan(self):
        """ Test for attempting to edit a plan that does not exist """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/edit-plan/16', follow_redirects=True)
        self.assertIn("You don&#39;t have edit access to this plan", result.data)
        self.assertIn("Plans", result.data)
        self.assertNotIn("Event name:", result.data, "Showing form for nonexistant plan")
        self.assertNotIn("Event Location Name:", result.data, "Showing form for nonexistant plan")

    def test_edit_plan_no_access(self):
        """ Test for attempting to edit a plan that user does not own """
        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/edit-plan/3', follow_redirects=True)
        self.assertIn("You don&#39;t have edit access to this plan", result.data)
        self.assertIn("Plans", result.data)
        self.assertNotIn("Event name:", result.data, "Showing form for nonexistant plan")
        self.assertNotIn("Event Location Name:", result.data, "Showing form for nonexistant plan")

    def test_add_friends_form(self):
        """ Test the adding friends form """
        
        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/add-friends/1', follow_redirects=True)

        self.assertIn("First Name", result.data)
        self.assertNotIn("Plans", result.data)

    def test_more_add_friends(self):
        """ Test the adding more friends form """
        
        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/add-more-friends/2', follow_redirects=True)

        self.assertIn("First Name", result.data)
        self.assertNotIn("Plans", result.data)


    def test_add_friends(self):
        """ Test adding friends updates database and profile page"""

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.post('/add-friends/1',
                                    data={'fname1': 'Kim',
                                          'lname1': 'Kardashian',
                                           'email1': 'kimk@gmail.com',
                                           'phone1': '3451234567'},
                                    follow_redirects=True)

        # Check friend was added to profile page
        self.assertIn("Kim Kardashian", result.data)

        plan = Plan.query.get(1)
        self.assertIn("Kim", plan.invitees[0].first_name)


    def test_add_friends_redirect(self):
        """ Test that add friends redirects to profile if friends have already been added """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/add-friends/2', follow_redirects=True)

        # Check to see whether page redirect to profile instead of add friends page
        self.assertIn("Plans", result.data)
        self.assertIn("Night Out", result.data)
        self.assertNotIn("First Name", result.data)

    def test_delete_plan_form(self):
        """ Test deletion confirmation page """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.get('/delete-plan/2', follow_redirects=True)

        self.assertIn("Are you sure", result.data)
        self.assertNotIn("Plans", result.data)

    def test_delete_plan(self):
        """ Test plan deletion, plan will no longer appear in user's profile """

        # Load in user2 (with plans) into session
        with self.client as c:
            with c.session_transaction() as session:
                session['current_user'] = "sally@gmail.com"

        result = self.client.post('/delete-plan/2', follow_redirects=True)

        self.assertIn("has been deleted", result.data)
        self.assertNotIn("Roman Theater", result.data)


if __name__ == "__main__":
    # Call testing function to run
    unittest.main()
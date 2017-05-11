""" Night Out """

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import *
import datetime
import requests
from urllib import urlencode, quote
import os


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined



# Yelp Stuff
def get_yelp_bearer_token():
    """ Cache yelp token id """

    # OS environ for client ID would not be accepted on Yelp side
    data = urlencode({
    'client_id': 's50ybEKVTcgO0rhu7bXKHA',
    'client_secret': os.environ['YELP_CLIENT_SECRET'],
    'grant_type': 'client_credentials',
    })

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    host = 'https://api.yelp.com'
    path = '/oauth2/token'
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    response = requests.request("POST", url, data=data, headers=headers)
    print response.json()
    bearer_token = response.json()['access_token']
    return bearer_token


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/create-account')
def create_account():
    """ Allows user to create a new account """
    return render_template('create_account.html')

@app.route('/create-account', methods=['POST'])
def create_new_user():
    """ Checks user email is new and processes registration 

    Adds plans that user was previously an invitee
    """
    
    # Extract all data from account creation form
    user_email = request.form.get('email')
    user_password = request.form.get('password')
    user_first_name = request.form.get('first_name')
    user_last_name = request.form.get('last_name')
    user_zip = request.form.get('zip_code')


    user = User.query.filter_by(email=user_email).all()

    # User email already used for a user
    if user:
        flash("User email already exists")
        return redirect('/login-form')
    # Create new user and log in
    else:
        new_user = User(email=user_email, password=user_password, 
                        first_name=user_first_name, last_name=user_last_name, 
                        zipcode=user_zip)
        db.session.add(new_user)
        db.session.commit()
        session['current_user'] = user_email
        flash('You are now registered and logged in!')


    # Add previously invited plans
        return redirect('/')

@app.route('/logout')
def logout():
    """Logs out user"""
    del session['current_user']
    flash("You are now logged out.")
    return redirect('/login-form')

@app.route('/login-form')
def login():
    """Prompts user to log in"""
    return render_template('login_form.html')


@app.route('/check-login', methods=['POST'])
def check_login():
    """Check if email in users table"""

    # Extract data from form
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    # Look for user in database and match password
    try:
        user = User.query.filter_by(email=user_email).one()
        if user.password == user_password:
            session['current_user'] = user_email
            flash('You are now logged in!')
            return redirect('/new-plan')
        else:
            flash('Wrong password!')
            return redirect('/login-form')

    # If user does not exist, re-direct to account creation
    except:
        flash("No user with that email")
        return redirect('/create-account')

@app.route('/new-plan')
def new_plan():
    """ User creates a new plan """
    return render_template('add_plan.html')

@app.route('/new-plan', methods=['POST'])
def add_new_plan():
    """ Adds event to user's new plan """

    # Extract data from plan form
    new_plan_name = request.form.get('plan_name')
    new_event_name = request.form.get('event_name')
    new_plan_date = request.form.get('event_date')
    new_plan_time = request.form.get('event_time')
    new_event_datetime = datetime.datetime.strptime(new_plan_date + " " + new_plan_time, "%Y-%m-%d %H:%M")
    new_plan_location = request.form.get('location')
    new_plan_address = request.form.get('address')
    new_plan_state = request.form.get('state')
    new_plan_city = request.form.get('city')
    new_plan_zipcode = request.form.get('zipcode')

    # If user chooses to not name plan right away - defaults to the event name
    if new_plan_name == "":
        new_plan_name = new_event_name

    current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

    # Create new plan object with plan attributes
    new_plan = Plan(plan_user_creator=current_user_id, plan_name=new_plan_name, 
                    event_name=new_event_name, event_time=new_event_datetime, 
                    event_location=new_plan_location, event_address=new_plan_address, 
                    event_state=new_plan_state, event_city=new_plan_city, 
                    event_zipcode=new_plan_zipcode)
    
    # Add plan to Plan database
    db.session.add(new_plan)
    db.session.flush()
    current_plan_id = new_plan.plan_id
    db.session.commit()

    # Add association between User and Plan in UserPlan database
    new_userplan = UserPlan(user_id=current_user_id, plan_id=current_plan_id)
    db.session.add(new_userplan)
    db.session.commit()

    # Change this to add restaurant when this is good
    return redirect('/choose-restaurant/'+str(current_plan_id))

@app.route('/choose-restaurant/<plan_id>')
def choose_restaurant(plan_id):
    """ Allows a user to choose a restaurant to add to plan """
    # Will default to two hours before event and one mile radius around location
    # Future iteration - ask user how far willing to go and how much earlier they would like to meet
    current_plan = Plan.query.get(plan_id)
    location = current_plan.event_address+" "+current_plan.event_city+" "+current_plan.event_state+ " "+current_plan.event_zipcode
    open_at_hour = current_plan.event_time.hour - 2

    headers = {
        'Authorization': 'Bearer %s' % app.yelp_bearer_token,
    }

    bar_url_params = {
        'term': 'bars',
        'location': location.replace(' ', '+'),
        'limit': 10,
        'radius': 1600,
    }


    b = requests.request('GET', 'https://api.yelp.com/v3/businesses/search', headers=headers, params=bar_url_params)
    print b
    bars = b.json()

    rest_url_params = {
        'term': 'restaurants',
        'location': location.replace(' ', '+'),
        'limit': 10,
        'radius': 1600,
    }

    r = requests.request('GET', 'https://api.yelp.com/v3/businesses/search', headers=headers, params=rest_url_params)
    print r
    restaurants = r.json()

    print bars
    print restaurants

    return render_template("choose_business.html", restaurants=restaurants, bars=bars, current_plan_id=plan_id)

@app.route('/choose-restaurant/<plan_id>', methods=['POST'])
def add_plan_restaurant(plan_id):
    """ Adds restaurant or bar to user's current plan """
    headers = {
        'Authorization': 'Bearer %s' % app.yelp_bearer_token,
    }

    chosen_id = request.form.get('event_food')

    chosen = requests.request('GET', 'https://api.yelp.com/v3/businesses/'+chosen_id, headers=headers)
    food_chosen = chosen.json()

    print food_chosen
    # Get current plan and update with yelp listing details
    current_plan = Plan.query.get(plan_id)

    current_plan.food_time = current_plan.event_time - datetime.timedelta(hours=2)
    current_plan.food_name = food_chosen['name']
    current_plan.food_address = food_chosen['location']['address1']
    current_plan.food_city = food_chosen['location']['city']
    current_plan.food_state = food_chosen['location']['state']
    current_plan.food_zipcode = food_chosen['location']['zip_code']
    current_plan.food_longitude = food_chosen['coordinates']['longitude']
    current_plan.food_latitude = food_chosen['coordinates']['latitude']

    db.session.commit()

    return redirect('/')


@app.route('/profile')
def user_profile():
    """ Dashboard for all user's plans """

    # This needs de-bugging and fixing oops
    current_user = User.query.filter_by(email=session['current_user']).first()
    plans = current_user.plans
    print plans

    return render_template('all_plans.html', plans=plans)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    app.yelp_bearer_token = get_yelp_bearer_token()

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
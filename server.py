""" Night Out """

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request, flash, session, jsonify, g, url_for
from functools import wraps
from model import *
import datetime
import requests
from urllib import urlencode, quote
import os
import bcrypt
import json
import sendgrid
from sendgrid.helpers.mail import *
from helper_sorts import *


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


# API HELPER FUNCTIONS
def get_yelp_bearer_token():
    """ Call Yelp API to attain a bearer token """

    # OS environ for client ID would not be accepted on Yelp side
    data = urlencode({
    'client_id': os.environ['YELP_CLIENT_ID'],
    'client_secret': os.environ['YELP_CLIENT_SECRET'],
    'grant_type': 'client_credentials',
    })

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    host = 'https://api.yelp.com'
    path = '/oauth2/token'
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    response = requests.request("POST", url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    print bearer_token
    return bearer_token


def send_email(plan_id, invitee_email, invitee_first_name, invitee_last_name):
    """ Send email to invited guests """
    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])

    plan = Plan.query.get(plan_id)
    

    # Set up email settings
    from_email = Email("donotreply@nightout.com", "Night Out Concierge")
    subject = "Plan for " + plan.event_name + " on " + plan.event_time.strftime('%x')
    to_email = Email(invitee_email, invitee_first_name + " " + invitee_last_name)

    # HTML to represent body of email
    html_header="<h3>"+plan.event_time.strftime('%x') + " " + plan.plan_name+ "</h3>"
    html_event = "<h4>" + plan.event_time.strftime('%-I:%M %p')+ ": " + plan.event_name + "</h4>"
    
    html_evlocation = ""
    if plan.event_location:
        html_evlocation = "<p>"+ plan.event_location + "</p>"
    html_evaddress = "<p>" + plan.event_address + "</p><p>" + plan.event_city+ ", " + plan.event_state+ " " + plan.event_zipcode

    html_food = ""
    if (plan.food_name) and (plan.food_time):
        html_food = "<h4>" + plan.food_time.strftime('%-I:%M %p')+": "+plan.food_name+"</h4><p>"+plan.food_address+"</p><p>"+plan.food_city+", "+plan.food_state+" "+plan.food_zipcode+"</p>"

    html_string = html_header+html_food+html_event+html_evlocation+html_evaddress

    content = Content("text/html", "<html><body>" + html_string + "</body></html>")

    mail = Mail(from_email, subject, to_email, content)

    # Send e-mail and get status message
    data = mail.get()
    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'current_user' in session:
            return redirect('/login-form')
        return f(*args, **kwargs)
    return decorated_function

def plan_access(plan_id):
    """ Helper function to check user has access to the url for specific plan id 

    Additionally, check that plan_id exists
    """
    # Get plan_id from the url of that route
    plan = Plan.query.get(plan_id)

    # If plan does not exist in database
    if not plan:
        return False

    # Get user's id from session
    current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

    # Redirect user back to their profile if 
    if plan.plan_user_creator != current_user_id:
        return False
    return True

    
@app.route('/')
def index():
    """Homepage."""
    if 'current_user' in session:
        return redirect('/profile')
    return render_template("homepage.html")


@app.route('/create-account')
def create_account():
    """ Allows user to create a new account """
    return render_template('create_account.html')

@app.route('/create-account', methods=['POST'])
def create_new_user():
    """ Checks user email is new and processes registration 

    Adds plans in which that user was previously an invitee
    """
    
    # Extract all data from account creation form
    user_email = request.form.get('email')
    user_password = request.form.get('password')
    user_first_name = request.form.get('first_name')
    user_last_name = request.form.get('last_name')

    # Encode password
    hashed = bcrypt.hashpw(user_password.encode('utf8'), bcrypt.gensalt(9))

    user = User.query.filter_by(email=user_email).all()

    # User email already used for a user
    if user:
        flash("User email already exists")
        return redirect('/login-form')
    # Create new user and log in
    else:
        new_user = User(email=user_email, password=hashed, 
                        first_name=user_first_name, last_name=user_last_name)
        # Add new user to the databased
        db.session.add(new_user)

        # Flush db to get new_user user_id
        db.session.flush()

        # Check if user has had previous invites and add them to userplans
        previously_invited = Invitee.query.filter_by(email=user_email).all()

        db.session.commit()
        # Loop through all previous invites and add user plans to associate to user
        if previously_invited:
            for previous_plan in previously_invited:
                new_user_plan = UserPlan(plan_id=previous_plan.plan_id, user_id=new_user.user_id)
                db.session.add(new_user_plan)
                db.session.commit()


        session['current_user'] = user_email
        flash('You are now registered and logged in!')

        return redirect('/profile')

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
        if bcrypt.checkpw(user_password.encode('utf8'), user.password.encode('utf8')):
            session['current_user'] = user_email
            flash('You are now logged in!')
            return redirect('/profile')
        else:
            flash('Wrong password!')
            return redirect('/login-form')

    # If user does not exist, re-direct to account creation
    except:
        flash("No user with that email")
        return redirect('/create-account')


@app.route('/profile')
@login_required
def user_profile():
    """ Dashboard for all user's plans 

    Orders plans by time to show past and current plans in profile
    """

    # Query database for all plans for a logged-in user
    current_user = User.query.filter_by(email=session['current_user']).first()
    plans = current_user.plans

    upcoming = []
    past = []
    now = datetime.datetime.now()

    # Distinguish between plans that are before and after now (based on datetime)
    for plan in plans:
        if plan.event_time >= now:
            upcoming.append(plan)
        else:
            past.append(plan)

    # MergeSort upcoming and past plans by date
    upcoming = mergesort_plans_by_date(upcoming)
    plans = mergesort_plans_by_date(past)

    current_user_id = current_user.user_id
    return render_template('all_plans.html', upcoming=upcoming, past=past, current_user=current_user_id)


@app.route('/new-plan')
@login_required
def new_plan():
    """ User creates a new plan """
    return render_template('add_plan.html')


@app.route('/new-plan', methods=['POST'])
@login_required
def add_new_plan():
    """ Adds event to user's new plan """

    # Extract data from plan form
    new_plan_name = request.form.get('plan_name')
    new_event_name = request.form.get('event_name')
    new_plan_date = request.form.get('event_date')
    new_plan_time = request.form.get('event_time')
    new_event_datetime = datetime.datetime.strptime(new_plan_date + " " + new_plan_time, "%Y-%m-%d %H:%M")
    new_plan_location = request.form.get('location')
    new_plan_number = request.form.get('number')
    new_plan_street = request.form.get('street')
    new_plan_state = request.form.get('state')
    new_plan_city = request.form.get('city')
    new_plan_zipcode = request.form.get('zipcode')
    new_plan_lat = request.form.get('event_lat')
    new_plan_long = request.form.get('event_long')

    # Strip off extra address details added by Google Autofill
    new_plan_location = new_plan_location.split(",")[0]

    new_plan_address = new_plan_number + " " + new_plan_street

    # If user chooses to not name plan right away - defaults to the event name
    if new_plan_name == "":
        new_plan_name = new_event_name

    new_plan_long = float(new_plan_long)
    new_plan_lat = float(new_plan_lat)

    current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

    # Create new plan object with plan attributes
    new_plan = Plan(plan_user_creator=current_user_id, plan_name=new_plan_name, 
                    event_name=new_event_name, event_time=new_event_datetime, 
                    event_location=new_plan_location, event_address=new_plan_address, 
                    event_state=new_plan_state, event_city=new_plan_city, 
                    event_zipcode=new_plan_zipcode, event_longitude=new_plan_long, event_latitude=new_plan_lat)
    
    # Add plan to Plan database
    db.session.add(new_plan)
    db.session.flush()
    current_plan_id = new_plan.plan_id
    db.session.commit()

    # Add association between User and Plan in UserPlan database
    new_userplan = UserPlan(user_id=current_user_id, plan_id=current_plan_id)
    db.session.add(new_userplan)
    db.session.commit()

    # Choose a restaurant
    return redirect('/choose-restaurant/'+str(current_plan_id))

@app.route('/edit-plan/<plan_id>')
@login_required
def edit_plan(plan_id):
    """ User edits an existing plan they own """

    if plan_access(plan_id):  
        # Pull current user from session and plan id from route
        current_user = User.query.filter_by(email=session['current_user']).first().user_id
        plan = Plan.query.get(plan_id)

        # Separate date and time from datetime object in database
        plan_datetime = plan.event_time
        plan_date = plan_datetime.date()
        plan_date = plan_date.strftime("%Y-%m-%d")
        plan_time = plan_datetime.time()
        plan_time = plan_time.strftime("%H:%M")

        return render_template('edit_plan.html', plan=plan, plan_date=plan_date, plan_time=plan_time)
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/edit-plan/<plan_id>', methods=['POST'])
@login_required
def edit_event_plan(plan_id):
    """ Adds event to user's new plan """

    if plan_access(plan_id):
        plan = Plan.query.get(plan_id)

        # Extract data from plan form
        new_plan_name = request.form.get('plan_name')
        new_event_name = request.form.get('event_name')
        new_plan_date = request.form.get('event_date')
        new_plan_time = request.form.get('event_time')
        new_event_datetime = datetime.datetime.strptime(new_plan_date + " " + new_plan_time, "%Y-%m-%d %H:%M")
        new_plan_location = request.form.get('location')
        new_plan_number = request.form.get('number')
        new_plan_street = request.form.get('street')
        new_plan_state = request.form.get('state')
        new_plan_city = request.form.get('city')
        new_plan_zipcode = request.form.get('zipcode')
        new_plan_lat = request.form.get('event_lat')
        new_plan_long = request.form.get('event_long')

        # Strip off extra address details added by Google Autofill
        new_plan_location = new_plan_location.split(",")[0]

        # Mark if event's location has changed to allow user to choose a different restaurant
        if new_plan_location != plan.event_location:
            different_location = True
        else:
            different_location = False

        new_plan_address = new_plan_number + " " + new_plan_street

        # If user chooses to not name plan right away - defaults to the event name
        if new_plan_name == "":
            new_plan_name = new_event_name

        current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

        # Edit plan object with plan attributes
        plan.plan_name = new_plan_name
        plan.event_name = new_event_name
        plan.event_time = new_event_datetime
        plan.event_location = new_plan_location
        plan.event_address = new_plan_address
        plan.event_state = new_plan_state
        plan.event_city = new_plan_city
        plan.event_zipcode = new_plan_zipcode
        plan.event_longitude = float(new_plan_long)
        plan.event_latitude = float(new_plan_lat)

        db.session.commit()

        if different_location == False:
            return redirect('/profile')
        else:
            return redirect('/choose-restaurant/'+str(plan.plan_id))
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/yelp.json', methods=["POST"])
@login_required
def choose_restaurant():
    """ Allows a user to choose a restaurant to add to plan """


    # Get user preferences from first "customize" form
    plan_id = int(request.form.get("plan_id"))
    business = str(request.form.get("bar_or_rest"))
    time_before = float(request.form.get("time_before"))
    distance = float(request.form.get("distance"))

    current_plan = Plan.query.get(plan_id)

    # Calculate time to meet at restaurant/ bar and save it to plan
    food_time = current_plan.event_time - datetime.timedelta(hours=time_before)
    current_plan.food_time = food_time
    db.session.commit()

    # Calculating parameters for Yelp API call
    location = current_plan.event_address+" "+current_plan.event_city+" "+current_plan.event_state+ " "+current_plan.event_zipcode
    radius = int(distance * 1600)
    unix_time = int((food_time - datetime.datetime(1970, 1, 1)).total_seconds())

    headers = {
        'Authorization': 'Bearer %s' % app.yelp_bearer_token,
    }

    rest_url_params = {
        'term': business,
        'location': location.replace(' ', '+'),
        'limit': 50,
        'radius': radius,
    }

    try:
        r = requests.request('GET', 'https://api.yelp.com/v3/businesses/search', headers=headers, params=rest_url_params)
        response = r.json()
        businesses = response['businesses']
        
        # Get current user's plans to determine which business locations they have visited
        current_user = User.query.filter_by(email=session['current_user']).first()
        plans = current_user.plans
        prior_businesses = set([])

        # Loop through plans to add previously visited businesses
        # Businesses are considered unique based on a combination of name and zipcode
        for plan in plans:
            if plan.food_name:
                prior_businesses.add(plan.food_name+str(plan.food_zipcode))

        # Loop through businesses and determine which user has selected in previous plans
        for business in businesses:
            if business['name']+str(business['location']['zip_code']) in prior_businesses:
                business['prior'] = True
            else:
                business['prior'] = False

        return jsonify(businesses)
    except:
        flash("Something went wrong! Please try again later.")
        return redirect('/profile')


@app.route('/choose-restaurant/<plan_id>')
@login_required
def customize_restaurant(plan_id):
    """ Allows a user to customize distance from location, time meeting and whether a restaurant or bar """
    if plan_access(plan_id):
        return render_template("customize_business.html", current_plan_id=plan_id)
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/choose-restaurant/<plan_id>', methods=['POST'])
@login_required
def add_plan_restaurant(plan_id):
    """ Adds restaurant or bar to user's current plan """
    if plan_access(plan_id):
        try: 
            chosen_id = request.form.get('event_food')
            food_chosen = json.loads(chosen_id)


            # Get current plan and update with yelp listing details
            current_plan = Plan.query.get(plan_id)

            current_plan.food_name = food_chosen['name']
            current_plan.food_address = food_chosen['location']['address1']
            current_plan.food_city = food_chosen['location']['city']
            current_plan.food_state = food_chosen['location']['state']
            current_plan.food_zipcode = food_chosen['location']['zip_code']
            current_plan.food_longitude = food_chosen['coordinates']['longitude']
            current_plan.food_latitude = food_chosen['coordinates']['latitude']

            db.session.commit()

            return redirect('/add-friends/'+str(plan_id))

        except:
            flash("Something went wrong. Please try again later.")
            return redirect('/profile')
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/add-friends/<plan_id>')
@login_required
def add_friends(plan_id):
    """ Add users friends to plan """
    if plan_access(plan_id):
        plan = Plan.query.get(plan_id)

        # If user got re-directed here through editing restaurant, take back to profile
        if plan.invitees:
            return redirect('/profile')

        else:
            return render_template("add_friends.html", plan=plan)
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/add-more-friends/<plan_id>')
@login_required
def add_more_friends(plan_id):
    """ Add more users friends to plan through 'add friends' button """
    if plan_access(plan_id):  
        plan = Plan.query.get(plan_id)
        return render_template("add_friends.html", plan=plan)

    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/add-friends/<plan_id>', methods=['POST'])
@login_required
def add_invitees(plan_id):
    """ Add users friends to plan """
    if plan_access(plan_id): 
        current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

        # Check if user inputted any friends
        added_friends = False

        for friend in range(12):
            if request.form.get('fname'+str(friend)):
                added_friends = True
                fname = request.form.get('fname'+str(friend))
                lname = request.form.get('lname'+str(friend))
                email = request.form.get('email'+str(friend))
                phone = request.form.get('phone'+str(friend))
                new_invitee = Invitee(plan_id=plan_id, user_id=current_user_id, 
                                    first_name=fname, last_name=lname, email=email,
                                    phone=phone)
                db.session.add(new_invitee)

                # E-mail user notifying of being added to plan
                send_email(plan_id=plan_id, invitee_email=email, invitee_first_name=fname, invitee_last_name=lname)
                flash("Email invite sent to {}".format(email))

                # Check if invitee has an account and add plan to their userplan
                invitee_user = User.query.filter_by(email=email).first()

                if invitee_user:
                    new_user_plan = UserPlan(plan_id=plan_id, user_id=invitee_user.user_id)
                    db.session.add(new_user_plan)
                
                db.session.commit()

        return redirect ('/profile')

    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/delete-plan/<plan_id>')
@login_required
def delete_plan_ask(plan_id):
    """ Double check that a user means to delete a plan record """
    if plan_access(plan_id): 
        plan = Plan.query.get(plan_id)
        return render_template("delete_plan.html", plan=plan)

    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/delete-plan/<plan_id>', methods=['POST'])
@login_required
def delete_plan_forever(plan_id):
    """ Double check that a user means to delete a plan record """
    if plan_access(plan_id): 
        plan = Plan.query.get(plan_id)

        db.session.delete(plan)
        db.session.commit()

        flash(plan.plan_name + "has been deleted")

        return redirect('/profile')
    else:
        flash("You don't have edit access to this plan")
        return redirect('/profile')


@app.route('/decline-plan/<plan_id>', methods=['POST'])
@login_required
def decline_plan(plan_id):
    """ Allows a user to delete a plan from their own profile but not the overall plan """
    current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

    userplan_decline = UserPlan.query.filter(UserPlan.plan_id == plan_id and UserPlan.user_id == current_user_id).all()

    for userplan in userplan_decline:
        db.session.delete(userplan)
    
    db.session.commit()

    return redirect('/profile')

@app.route('/event-frequency.json')
@login_required
def generate_chart_data():
    """ Uses user's plan data to create the data for a JS Chart """
    data_dict = {"datasets": [
                                {
                                    "label": "Events per Month",
                                    "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "backgroundColor": 'rgba(1, 1, 59, 0.8)' 
                                }],
                            "labels": ['January', 'February', 'March', 'April', 'May', 
                                        'June', 'July', 'August', 'September',
                                        'October', 'November', 'December'] }

    current_user = User.query.filter_by(email=session['current_user']).first()
    plans = current_user.plans

    # Tallies the amount of plans for each month
    for plan in plans:
        data_dict['datasets'][0]['data'][int(plan.event_time.month)-1] += 1

    return jsonify(data_dict)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app, 'postgresql:///eventplans')

    app.yelp_bearer_token = 'WllJxLDGOspRQnGbwsoqd9CFqeW8_LshxaRo1WZXWbTJ5-zCePPbNwW61x1NCJiX9-RIh7KMiP-3l7RxJtrqnczHAILypbXeduWluvi3zK0OTUorLHk_9E3TbIMTWXYx'

    app.run(port=5000, host='0.0.0.0')
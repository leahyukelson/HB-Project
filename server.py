""" Night Out """

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import *
import datetime


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

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
            return redirect('/plans')
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
    new_plan_name = request.form.get('plan_name')
    new_event_name = request.form.get('event_name')
    new_plan_date = request.form.get('event_date')
    new_plan_time = request.form.get('event_time')
    print("date", new_plan_date)
    print("time", new_plan_time)
    new_event_datetime = datetime.datetime.strptime(new_plan_date + " " + new_plan_time, "%Y-%m-%d %H:%M")
    new_plan_location = request.form.get('location')
    new_plan_address = request.form.get('address')
    new_plan_state = request.form.get('state')
    new_plan_city = request.form.get('city')
    new_plan_zipcode = request.form.get('zipcode')

    if new_plan_name == "":
        new_plan_name = new_event_name

    current_user_id = User.query.filter_by(email=session['current_user']).first().user_id

    new_plan = Plan(plan_user_creator=current_user_id, plan_name=new_plan_name, event_name=new_event_name, event_time=new_event_datetime, event_location=new_plan_location, event_address=new_plan_address, event_state=new_plan_state, event_city=new_plan_city, event_zipcode=new_plan_zipcode)

    # DEBUG
    
    db.session.add(new_plan)
    db.session.flush()
    
    print("PLAN!!!!!", new_plan)

    current_plan_id = new_plan.plan_id
    new_userplan = UserPlan(user_id=current_user_id, plan_id=current_plan_id)

    db.session.add(new_plan)
    db.session.add(new_userplan)

    # Change this to add restaurant when this is good
    return redirect('/')


# @app.route('/plans')
# def user_plan():
#     """ Dashboard for all user's plans """

#     # This needs de-bugging and fixing oops
#     current_user_id = User.query.filter_by(email=session['current_user']).first().user_id
#     plans = db.session.query(UserPlan.plan).filter(UserPlan.user_id==current_user_id).join(User).join(Plan)
#     return render_template('all_plans.html')

# def example_plan():
#     """Load example plan into database."""

#     # New Data each time
#     User.query.delete()
#     Plan.query.delete()
#     UserPlan.query.delete()

#     user = User(user_id=1, first_name='Leah', last_name='Yukelson', email='leah@gmail.com', password='leah', zipcode='94114')
#     event_time = datetime.datetime.strptime("01-Jan-2018", "%d-%b-%Y")
#     plan = Plan(plan_user_creator=1, event_time=event_time, plan_name="NYE", event_name="New Year's Eve", event_address="1 Market St.", event_city="San Francisco", event_state="CA", event_zipcode="94105")
#     userplan = UserPlan(user_id=1, plan_id=2)
#     event_time = datetime.datetime.strptime("10-Dec-2017", "%d-%b-%Y")
#     plan2 = Plan(plan_user_creator=1, event_time=event_time, plan_name="BDay", event_name="Leahs Birthday Party", event_address="2259 Kalakaua Ave.", event_city="Honolulu", event_state="HI", event_zipcode="96815")
#     userplan2 = UserPlan(user_id=1, plan_id=2)
#     # We need to add to the session or it won't ever be stored
    
#     db.session.add(user)
#     db.session.add(plan)
#     db.session.add(plan2)
#     db.session.add(userplan)
#     db.session.add(userplan2)

#     # Once we're done, we should commit our work
#     db.session.commit()

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # example_plan()

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
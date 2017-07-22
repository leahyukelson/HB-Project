"""Models and database functions """

from flask_sqlalchemy import SQLAlchemy
import bcrypt

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of Event app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    zipcode = db.Column(db.String(15), nullable=True)

    # Define relationship to plan
    plans = db.relationship("Plan",
                            secondary = "userplans",
                           backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

class Plan(db.Model):
    """Plan for an event."""

    __tablename__ = "plans"

    plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plan_user_creator = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    plan_name = db.Column(db.String(100), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_location = db.Column(db.String(100))
    event_address = db.Column(db.String(100), nullable=False)
    event_city = db.Column(db.String(50), nullable=False)
    event_state = db.Column(db.String(50), nullable=False)
    event_zipcode = db.Column(db.String(15), nullable=False)
    event_longitude = db.Column(db.Float)
    event_latitude = db.Column(db.Float)
    food_time = db.Column(db.DateTime)
    food_name = db.Column(db.String(100))
    food_address = db.Column(db.String(100))
    food_city = db.Column(db.String(50))
    food_state = db.Column(db.String(50))
    food_zipcode = db.Column(db.String(15))
    food_latitude = db.Column(db.Float)
    food_longitude = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Plan event_time=%s plan_id=%s event_name=%s>" % (self.event_time, self.plan_id, self.event_name)    


class Invitee(db.Model):
    """ Friends invited to plans - not necessarily users"""

    __tablename__ = "invitees"

    invitee_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.plan_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(64))

    # Define relationship to plan
    plan = db.relationship("Plan",
                           backref=db.backref("invitees",
                                              order_by=invitee_id))

    # Define relationship to invitee's friend
    friend = db.relationship("User",
                           backref=db.backref("invitees",
                                              order_by=invitee_id))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Invitee invitee_id=%s plan_id=%s>" % (self.invitee_id, self.plan_id)


class UserPlan(db.Model):
    """Association table to associate user to plan. """

    __tablename__ = "userplans"

    user_plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.plan_id'))


    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<User Plan user_plan_id=%s user_id=%s plan_id=%s>"
        return s % (self.user_plan_id, self.user_id, self.plan_id)


##############################################################################
# Helper functions

def fill_example_data():
    """ Fill database with sample data to start with """

    # User without plans
    user1 = User(first_name="Rachel", last_name="Ray", email="rachel@gmail.com", password=bcrypt.hashpw("word", bcrypt.gensalt(9)), zipcode="12345")

    # User with plans
    user2 = User(first_name="Sally", last_name="Silly", email="sally@gmail.com", password=bcrypt.hashpw("passpass", bcrypt.gensalt(9)), zipcode="56789")

    # User with plans
    user3 = User(first_name="Sam", last_name="Silly", email="sammy@gmail.com", password=bcrypt.hashpw("passhash", bcrypt.gensalt(9)), zipcode="56789")

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    # Plan with no food component
    plan1 = Plan(plan_user_creator=2, plan_name="Night Out", event_name="Concert", 
                event_time="2018-10-03 21:30:00", event_location="Greek Theater", event_address="2001 Gayley Rd.", event_city="Berkeley",
                event_state="CA", event_zipcode="94720")

    # Plan with food component
    plan2 = Plan(plan_user_creator=2, plan_name="Night Out", event_name="Concert", 
                event_time="2018-10-03 21:30:00", event_location="Roman Theater", event_address="2001 Gayley Rd.", event_city="Berkeley",
                event_state="CA", event_zipcode="94720", food_time="2018-10-03 20:00:00", food_name="Smoke's Poutinerie", food_address="2518 Durant Ave",
                food_city="Berkeley", food_state="CA", food_zipcode="94704")

    # Plan with food component
    plan3 = Plan(plan_user_creator=3, plan_name="Night Out", event_name="Concert", 
                event_time="2018-10-03 21:30:00", event_location="Greek Theater", event_address="2001 Gayley Rd.", event_city="Berkeley",
                event_state="CA", event_zipcode="94720", food_time="2018-10-03 20:00:00", food_name="Smoke's Poutinerie", food_address="2518 Durant Ave",
                food_city="Berkeley", food_state="CA", food_zipcode="94704")

    # Plan in the past
    plan4 = Plan(plan_user_creator=2, plan_name="Night Out", event_name="Concert", 
                event_time="2018-10-03 21:30:00", event_location="Greek Theater", event_address="2001 Gayley Rd.", event_city="Berkeley",
                event_state="CA", event_zipcode="94720", food_time="2018-10-03 20:00:00", food_name="Smoke's Poutinerie", food_address="2518 Durant Ave",
                food_city="Berkeley", food_state="CA", food_zipcode="94704")

    db.session.add(plan1)
    db.session.add(plan2)
    db.session.add(plan3)
    db.session.add(plan4)
    db.session.commit()

    # Userplan for user1 to associate with plans
    userplan1 = UserPlan(user_id=2, plan_id=1)
    userplan2 = UserPlan(user_id=2, plan_id=2)
    userplan3 = UserPlan(user_id=3, plan_id=3)
    userplan4 = UserPlan(user_id=2, plan_id=4)

    db.session.add(userplan1)
    db.session.add(userplan2)
    db.session.add(userplan3)
    db.session.add(userplan4)
    db.session.commit()

    # Create invitees for plan2
    invitee1 = Invitee(plan_id=2, user_id=2, first_name="Bob", last_name="Bobby", email="bobby@gmail.com", phone="3458761234")
    invitee2 = Invitee(plan_id=2, user_id=2, first_name="Joe", last_name="Shmo", email="joeee@gmail.com", phone="3452309876")

    db.session.add(invitee1)
    db.session.add(invitee2)
    db.session.commit()

def connect_to_db(app, psql_server):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = psql_server
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app, 'postgresql:///eventplans')
    print "Connected to DB."
    db.create_all()
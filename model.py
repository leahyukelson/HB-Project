"""Models and database functions """

from flask_sqlalchemy import SQLAlchemy

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
    food_latitude = db.Column(db.Float)
    food_longitude = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Plan plan_id=%s event_name=%s>" % (self.plan_id, self.event_name)    


class Invitee(db.Model):
    """ Friends invited to plans - not necessarily users"""

    __tablename__ = "invitees"

    invitee_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.plan_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.column(db.Integer)
    email = db.column(db.String(64))

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

    # Define relationship to plan
    plan = db.relationship("Plan",
                           backref=db.backref("userplans",
                                              order_by=user_plan_id))

    # Define relationship to invitee's friend
    user = db.relationship("User",
                           backref=db.backref("userplans",
                                              order_by=user_plan_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<User Plan user_plan_id=%s user_id=%s plan_id=%s>"
        return s % (self.user_plan_id, self.user_id, self.plan_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///eventplans'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
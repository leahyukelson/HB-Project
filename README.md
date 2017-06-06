# Night Out

![Night Out](https://github.com/leahyukelson/Night-Out/blob/master/static/nightout_t.png)

Night Out is an easy way to create a plan with friends around an event. Users input their pre-planned event into the application which generates listings of bars or restaurants. The listings can be sorted by distance, price or Yelp rating to simplify the choosing process. When the plan is created, users can add their friends, regardless if they are users, to the plan so that everyone is on the same page. Participants get an email with the full itinerary listing the time and place to meet. Users of the app have all their plans in one convenient place on their profile page along with analytics on how often they are attending plans.

## Contents
* [Tech Stack](#tech)
* [Features](#feats)
* [Installation](#install)
* [About Me](#about)

## <a name="tech"></a>Tech Stack
Python, Flask, PostgreSQL, SQLAlchemy, JavaScript, Chart.js, jQuery, AJAX, Jinja2, Bootstrap, HTML5, CSS3
**APIs:** Yelp, SendGrid, Google Maps

## <a name="feats"></a>Features

###### Step 1: Create account
Rest assured, passwords are hashed in the back-end. If you have been invited to plans by existing users, those plans will get automatically pre-populated into your profile page.
![](https://github.com/leahyukelson/Night-Out/blob/master/screenshots/create-account.JPG "Create Account Screenshot")

###### Step 2: Check out your profile page
All your upcoming and past plans are housed here, sorted in reverse calendar order so you can what's coming soonest. Feel free to edit plans, choose a different restaurant or add more friends for plans that you have created. If you would no longer like to attend an event, decline plan. If the entire plan is cancelled, delete the plan and the plan will be removed off all users' profiles.
![](http://g.recordit.co/muj8d3sL0f.gif "Profile Page Screenshot")

###### User Analytics
Chart JS created with user's data to outline user's scheduled events per month.
![](https://github.com/leahyukelson/Night-Out/blob/master/screenshots/analytics.JPG "Create Account Screenshot")

###### Step 3: Create a new plan
Enter details of pre-planned event - concert, movie showing, author talk, or whatever else you're attending. Google Maps API autofill makes it easier by helping to fill in address based on location's event name.
![](http://g.recordit.co/xyoeyzIim8.gif "Create Plan Screenshot")

###### Step 4: Customize pre-event meeting place
Choose whether to meet at a restaurant or bar, how far away you're willing to look and how long before the event you'd like to meet. Customizations are sent to the Yelp API and returns up to 50 different business locations. When business results come back, sort on price, distance or Yelp rating to choose the best place to meet. Businesses you have visited before are highlighted for easy re-selection. 
![](http://g.recordit.co/pjcVN3eBAx.gif "Customize Business Screenshot")

###### Step 5: Add friends to plan
Friends will get an email itinerary of the night's agenda! If a friend's email is signed up as a user, the plan will get populated in their profile.
![](https://github.com/leahyukelson/Night-Out/blob/master/screenshots/add-friends.JPG "Add Friends Screenshot")
![](https://github.com/leahyukelson/Night-Out/blob/master/screenshots/friend-email.JPG "Friends Email Screenshot")

## <a name="install"></a>Installation
Run Night Out on your machine:

Install PostgreSQL

Clone or fork this repo:

```
https://github.com/leahyukelson/Night-Out
```

Create and activate a virtual environment inside your LaterGator directory:

```
virtualenv env
source env/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```

Sign up with [SendGrid API](https://app.sendgrid.com/signup?id=71713987-9f01-4dea-b3d4-8d0bcd9d53ed)

Save your API key in a file called <kbd>secrets.sh</kbd> using this format:

```
export SENDGRID_API_KEY="YOURKEYHERE"
```

Source your keys from your secrets.sh file into your virtual environment:

```
source secrets.sh
```

Set up the database:

```
createdb eventplans
```

Run this python script to set up the data model:

```
python model.py
```

Run the app:

```
python server.py
```

You can now navigate to [localhost:5000/](localhost:5000) to start Night Out.

## <a name="about"></a>About Me
My name is Leah Yukelson and I am located in San Francisco, CA. This project was created during my time at Hackbright, a full-stack development accelerated program. I studied business information systems at Cal Poly SLO with an emphasis in computer science. After graduation, I went to work at Macy's doing search marketing; managing multi-million dollar budgets and making strategic marketing choices. While being on the business-facing side of advertising, I became more interested in how the technology works. I loved the logic problem solving aspect of my computer science classes at Cal Poly and decided to dive back into programming by self studying Python and then attending Hackbright Academy. I am currently interested in combining my interest in ad technology with full-stack web development.

Find me on [LinkedIn](https://www.linkedin.com/in/leahyukelson/)!
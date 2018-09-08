from eurypaa import app

import settings

from google.appengine.ext import db

from models import Post
from models import Registration
from models import AccessEntry

from flask import render_template
from flask import url_for
from flask import flash
from flask import redirect
from flask import request
from flask import session
from forms import PostForm
from forms import ContactForm
from forms import RegistrationForm
from forms import AccessEntryForm

from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

from decorators import login_required, acl_required

from google.appengine.api import users
from google.appengine.api import mail

import datetime

import stripe
from decimal import Decimal



stripe_test_keys = {
    'secret_key'      : "sk_test_mytestsecretkey",
    'publishable_key' : "pk_test_mytestpubkey"
}

stripe_live_keys = {
    'secret_key'      : "sk_live_mylivesecretkey",
    'publishable_key' : "pk_live_mytestpubkey"
}

stripe.api_key = stripe_live_keys['secret_key']


MAILCHIMP_API_KEY = "mymailchimpapikey"
MAILCHIMP_LIST_ID = "mymailchimplistid"


from postmonkey import PostMonkey
from postmonkey import MailChimpException


@app.route('/subscribe', methods=['POST'])
def subscribe():
    # We have passed the shared secret or we didn't care about it
    pm = PostMonkey(MAILCHIMP_API_KEY)
    
    # Get a posted email address
    email = request.form.get('email',None)
    if not email == None:
        # Send that off to Mailchimp
        pm = PostMonkey(MAILCHIMP_API_KEY)
        try:
            pm.listSubscribe(id=MAILCHIMP_LIST_ID, email_address=email,double_optin=False)
        except MailChimpException, e:
            print e.code  # 200
            print e.error # u'Invalid MailChimp List ID: 42'
            flash('Error: ' + str(e.error))
            return redirect(url_for('homepage'))
    flash('You are now subscribed!')
    return redirect(url_for('homepage'))


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/about')
@app.route('/about-bath')
def about():
    return render_template('about.html')


@app.route('/category/outreach')
@app.route('/news')
def list_posts():
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY when DESC")
    return render_template('news.html', posts=posts)


@app.route('/news/post/<slug>')
def get_post(slug):
    q = Post.all()
    q.filter("slug =", slug)
    post = q.get()
    if post is not None:
        return render_template('post.html', post=post)
    else:
        return render_template('404.html'), 404


@app.route('/add_access', methods=['GET','POST'])
@acl_required
def add_access():
    form = AccessEntryForm()
    if form.validate_on_submit():
        access = AccessEntry(first_name = form.first_name.data,
                             last_name  = form.last_name.data,
                             email      = form.email.data,
                             enabled    = False,
                             acl        = form.acl.data)
        access.put()
        flash('access entry added')
        return redirect(url_for('homepage'))
    return render_template('add_access.html', form=form)


#import csv2db
#
#@app.route('/process_csv')
#@acl_required
#def process_csv():
#    csv2db.csv2db("delta_registrations.csv")
#    return "Processed registrations csv!"


@app.route('/registrations.csv')
@acl_required
def registrations_csv():
    registrations = db.GqlQuery("SELECT * FROM Registration ORDER BY date_registered")
    return render_template('registrations.csv', registrations=registrations)


@app.route('/news/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post( title = form.title.data
                   , content = form.content.data
                   , author = users.get_current_user()
                   )
        post.put()
        flash('Post saved on database.')
        return redirect(url_for('list_posts'))
    return render_template('new_news.html', form=form)


def email_admin(details):
    sender = "EURYPAA 2016 Admin <appengineappid@gmail.com>"
    subject = "New Registration on EURYPAA 2016: %s" % details['first_name']
    message = mail.EmailMessage(sender=sender, subject=subject)
            
    message.to = "EURYPAA 2016 Admin <email@example.com>"
    
    message.body = """
    Dear Admin:
    
    There has been a new registration on EURYPAA 2016:

    first_name: %(first_name)s,
    last_name: %(last_name)s,
    registration_type: %(registration_type)s,
    mobile: %(mobile)s,
    email: %(email)s,
    country: %(country)s,
    sobriety_date: %(sobriety_date)s,
    ypaa_committee: %(ypaa_committee)s,
    fellowship: %(fellowship)s,
    special_needs: %(special_needs)s,
    of_service: %(of_service)s

    Stay awesome.
    """ % details
    
    message.send()


def email_user(details):
    sender = "EURYPAA 2016 Admin <appengineappid@gmail.com>"
    subject = "Registration confirmation at EURYPAA 2016"
    message = mail.EmailMessage(sender=sender, subject=subject)
            
    message.to = "%(first_name)s %(last_name)s <%(email)s>" % details

    message.body = """
    Dear %(first_name)s:
    
    This is your confirmation of registration at EURYPAA 2016!

    You have booked the '%(registration_type)s' option.

    Welcome aboard! We look forward to seeing you in Bath this August.
   
    Take care, and go well until then.

    Yours in Fellowship,
    
    EURYPAA 2016 Committee.
    """ % details
    
    message.send()


def send_contact_email(details):
    sender = "EURYPAA 2016 user <appengineappid@gmail.com>"
    subject = "EURYPAA 2016 Contact form, Subject: %(subject)s" % details
    message = mail.EmailMessage(sender=sender, subject=subject)
    message.to = "EURYPAA 2016 Admin <email@example.com>"
    message.body = ("\nNAME: %(name)s,\nEMAIL: %(email)s\n" + details['message']) % details
    message.send()


@app.route('/register', methods=['GET'])
def new_registration_1():
    return render_template('register_springboard.html')


@app.route('/register/<registration_type>', methods=['GET', 'POST'])
def new_registration_type(registration_type):
    form = RegistrationForm()
    if registration_type == 'sat_no_meal':
	session['registration_price'] = 1000
    elif registration_type == 'sat_with_meal':
	session['registration_price'] = 1900
    elif registration_type == 'full_no_meal':
	session['registration_price'] = 2000
    elif registration_type == 'full_with_meal':
	session['registration_price'] = 2900
    else:
	return render_template('404.html'), 404
    if form.validate_on_submit():
        if mail.is_email_valid(form.email.data):
            session['registration_type'] = registration_type
            session['first_name']     = form.first_name.data
            session['last_name']      = form.last_name.data
            session['mobile']         = form.mobile.data
            session['email']          = form.email.data
            session['sobriety_date']  = str(form.sobriety_date.data)
            session['ypaa_committee'] = form.ypaa_committee.data
            session['fellowship']     = form.fellowship.data
            session['special_needs']  = form.special_needs.data
            session['of_service']     = form.of_service.data
            session['country']        = form.country.data
            return redirect(url_for('new_registration_2', registration_type=registration_type))
        else:
            flash('Invalid email address')
            return redirect(url_for('new_registration_type', registration_type=registration_type))
    return render_template('new_registration_1.html', form=form, registration_type=registration_type)


@app.route('/register_2/<registration_type>')
def new_registration_2(registration_type):
    return render_template( 'new_registration_2.html'
                          , registration_type=registration_type
                          , amount=Decimal(session['registration_price'])
                          , email=session['email']
                          , key=stripe_live_keys['publishable_key']
                          )
    

def num_sobriety_twins(date):
    twins = db.GqlQuery("SELECT * FROM Registration WHERE sobriety_date = :1", date)
    return len([x for x in twins])

@app.route('/charge', methods=['POST'])
def charge():

    def str2date(date_string):
        """ Returns a datetime date given a valid date_string """
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    if request.method == 'POST':
        try:
            # Amount in pence
            
            customer = stripe.Customer.create(
                email=request.form['stripeEmail'],
                card=request.form['stripeToken']
            )
            charge = stripe.Charge.create(
                customer=customer.id,
                amount=Decimal(session['registration_price']),
                currency='gbp',
                description='Registration'
            )

            sob_date = None
            if session['sobriety_date'] != u'None':
               sob_date = str2date(session['sobriety_date'])

            registration = Registration(
                  first_name     = session['first_name']
                , last_name      = session['last_name']
                , mobile         = session['mobile']
                , email          = session['email']
                , sobriety_date  = sob_date
                , ypaa_committee = session['ypaa_committee']
                , fellowship     = session['fellowship']
                , special_needs  = session['special_needs']
                , of_service     = session['of_service']
                , country        = session['country']
                )
            registration.put()
            email_admin(session)
            email_user(session)
            flash("You are now registered!")

            if sob_date is not None:
                num_twins = num_sobriety_twins(str2date(session['sobriety_date']))
                if num_twins > 1:
                    if num_twins == 2:
                        flash("By the way, you have a sobriety twin coming to the convention!")
                    else:
                        flash("By the way, you have %d sobriety twins coming to the convention!" % (num_twins-1))

            return redirect(url_for('homepage'))

        except Exception, e:
            # TODO: Roll back transaction, registration
            #print "Payment not processed: %s" % e
            flash("Payment not processed. %s" % e)
            return redirect(url_for('new_registration_1'))
    return render_template('homepage.html')


@app.route('/news.atom')
def news_feed():
    feed = AtomFeed('EURYPAA 2016 News Posts',
                    feed_url=request.url, url=request.url_root)
    posts = Post.all()
    for post in posts:
        feed.add(post.title, unicode(post.content),
                 content_type='html',
                 author="EURYPAA2016 Admin",
                 published=post.when,
                 updated=post.when,
                 id=post.when)
    return feed.get_response()


@app.route('/planner')
def plan_your_trip():
    return render_template('plan_your_trip.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        details = { 'name'    : form.name.data
                  , 'email'   : form.email.data
                  , 'subject' : form.subject.data
                  , 'message' : form.message.data
                  }
        send_contact_email(details)
        flash('Message sent.')
        return redirect(url_for('homepage'))
    return render_template('contact_form.html', form=form)


@app.route('/donate')
def donate():
    return render_template( 'donate.html'
                          , key=stripe_live_keys['publishable_key']
                          , amount=2000
                          )

@app.route('/donate_charge', methods=['POST'])
def donate_charge():
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken']
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=Decimal(2000),
        currency='gbp',
        description='Donation'
    )
    flash('Thankyou for your donation!')
    return redirect(url_for('homepage'))

@app.route('/programme')
def programme():
    return render_template('timetable.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/accommodation')
def accommodation():
   return render_template('accommodation.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/map')
def campus_map():
    return render_template('campus_map.html')

@app.route('/banana')
def banana():
    return render_template('timetable.html')

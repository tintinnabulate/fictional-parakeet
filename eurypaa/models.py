from google.appengine.ext import db
from slugify import slugify

class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    when = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty(required=True)
    slug  = db.StringProperty(required=True)

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super(Post, self).__init__(*args, **kwargs)

class Registration(db.Model):
    date_registered = db.DateTimeProperty(auto_now_add=True)
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    mobile = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    sobriety_date = db.DateProperty(required=False)
    ypaa_committee = db.StringProperty(required=False)
    fellowship = db.StringProperty(required=True)
    special_needs = db.StringProperty(required=True)
    country = db.StringProperty(required=True)
    of_service = db.BooleanProperty(required=True)

class AccessEntry(db.Model):
    when = db.DateTimeProperty(auto_now_add=True)
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    enabled = db.BooleanProperty(required=True)
    acl = db.StringProperty(required=True)

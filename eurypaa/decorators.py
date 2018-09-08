from functools import wraps
from google.appengine.api import users
from flask import redirect, request
from models import AccessEntry

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view

def acl_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        else:
            allowed_users = AccessEntry.all()
            for u in allowed_users:
                if u.email == users.get_current_user().email() and u.enabled:
                    return func(*args, **kwargs)
        return redirect('/')
    return decorated_view

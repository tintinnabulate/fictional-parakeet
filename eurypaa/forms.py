from flask.ext import wtf
from flask.ext.wtf import validators
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import DateField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Optional
from datetime import datetime


class PostForm(wtf.Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])


class RegistrationForm(wtf.Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    mobile = StringField('Mobile Number', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    sobriety_date = DateField('Sobriety Date (YYYY mm dd)', format='%Y %m %d', validators=[Optional()])
    ypaa_committee = StringField('YPAA Committee')
    fellowship = StringField('Fellowship', validators=[DataRequired()])
    country = StringField('Country of origin', validators=[DataRequired()])
    special_needs = SelectField('Special Needs', choices=[ ('none', 'No special needs')
                                                         , ('hearing', 'Deaf/Hard of hearing')
                                                         , ('seizures', 'Seizures')
                                                         , ('vision', 'Blind/Low vision')
                                                         , ('wheelchair', 'Wheelchair access needed')
                                                         , ('other', 'Other') ]) 
    of_service = BooleanField('Yes I want to be of service at the convention')

    def validate_sobriety_date(form, field):
       if field.raw_data[0] == u'':
           return True
       else:
           try:
               d = datetime.strptime(field.raw_data[0], "%Y %m %d")
               return True
           except:
               raise validators.ValidationError('Sobriety date format must be: YYYY mm dd i.e. ' \
                                                'year month day separated by spaces. Leave '\
                                                'empty if you are from Al-Anon or do not have '\
                                                'a sobriety date')
               return False
         
class ContactForm(wtf.Form):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Your email address', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    recaptcha = wtf.RecaptchaField()

class AccessEntryForm(wtf.Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    acl = StringField('ACL fields (comma sep)', validators=[DataRequired()])


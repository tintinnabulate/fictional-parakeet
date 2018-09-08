# EURYPAA 2016 site

Web app written in Flask (Python web framework), targeted to run on Google App Engine.

The website currently resides at <https://foobar-1164.appspot.com>.

## Technologies used

* Flask-WTF for forms (see `eurypaa/forms.py`) 
* Google App Engine Datastore for
  the backend database (see `eurypaa/models.py`) 
* Stripe for secure payment processing
* Recaptcha for form spam
  prevention on the Contact Form (see `eurypaa/settings.py` for configuration,
  see `eurypaa/forms.py` for use) 
* Jinja2 templating (see
  `eurypaa/templates/base.html` for the base template from which the others
  inherit, see `eurypaa/templates/macros.html` for macros)
* Bootstrap.js for layout and responsiveness on mobile devices
* Git for version control
* postmonkey for Mailchimp integration

## Pages

* Homepage/splashpage: inherits from `eurypaa/templates/homepage-base.html`
  rather than base.html
* About: Uses Bootstrap carousel to display transitioning gallery of pictures
* Planner: 'Where is Bath?' Uses responsive iframe for Google Maps
* Registration: creates Registration() DB entries when Stripe payment form
  returns without exceptions (Note this is not necessarily an indication of
  successful transaction: see [TODO](#TODO)).  
* Contact form: Uses Recaptcha
* News page: creases Post() DB entries

## TODO

* Sign people up straight from Stripe: <https://github.com/optional-is/email2mailchimp>
* Only create Registration entry/Send email if Stripe charge has the right
  transaction type of "charge.succeeded"

## How to Deploy

To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create a
   project/app id. (App id and project id are identical)
2. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with

   ```
   appcfg.py -A <your-project-id> --oauth2 update .
   ```

3. Congratulations!  Your application is now live at your-app-id.appspot.com

If you have GNU Make installed you can run

```
make
```

to run the app locally, and

```
make deploy
```

to deploy the app to the live site. Make sure to change the file `Makefile` if
your-project-id differs from that given in the file.

## Maintenance

### Installing Libraries
See the [Third party
libraries](https://developers.google.com/appengine/docs/python/tools/libraries27)
page for libraries that are already included in the SDK.  To include SDK
libraries, add them in your app.yaml file. Other than libraries included in
the SDK, only pure python libraries may be added to an App Engine project.

To update the libraries in use, run 

```
pip install --upgrade -r requirements.txt -t lib/
```

Append other dependencies you may need into `requirements.txt` and re-run as necessary.

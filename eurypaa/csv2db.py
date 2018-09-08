from google.appengine.ext import db
from models import Registration
from datetime import datetime as d
import csv
import sys


def csv2db(csv_filename):
    def boolify(s):
        return {'True':True,'False':False}[s]
    def dateify(s):
        return d.strptime(s, "%d/%m/%Y").date() if s != 'none' else None
    with open(csv_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print row
            r = Registration(
                      first_name = row['first_name']
                    , last_name = row['last_name']
                    , mobile = row['mobile']
                    , email = row['email']
                    , sobriety_date = dateify(row['sobriety_date'])
                    , ypaa_committee = row['ypaa_committee']
                    , fellowship = row['member_of']
                    , special_needs = row['special_needs']
                    , country = row['country']
                    , of_service = boolify(row['of_service'])
                    )
            r.put()

if __name__ == '__main__':
    csv2db(sys.argv[1])

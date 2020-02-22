"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
import openaq

from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

api = openaq.OpenAQ()


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'Time {self.datetime} --- Value {self.value}'


def process_response(body):
    result = []
    for row in body['results']:
        utc_datetime, value = row['date']['utc'], row['value']
        result.append([utc_datetime, value])

    return result

def refresh_db(body):
    for row in body['results']:
        utc_datetime, value = row['date']['utc'], row['value']
        DB.session.add(Record(datetime=utc_datetime, value=value))


@APP.route('/')
def root():
    """Base view."""
    result = Record.query.filter(Record.value >= 10).all()
    
    return render_template("home.html", result=result)

#Part 3

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    refresh_db(body)
    DB.session.commit()
    return 'Data refreshed!'

#stretch goal part 2:
@APP.route('/countries')
def countries():
    """Base view."""
    status, body = api.countries()
    
    return render_template("countries.html", result=body["results"])

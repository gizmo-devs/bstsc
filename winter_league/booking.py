from datetime import datetime, date, time
from dateutil.parser import parse
import json, pytz
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, query_db
from .auth import login_required

bp = Blueprint('booking', __name__, url_prefix='/booking')



@bp.route('/')
@login_required
def index():
    return render_template('booking/index.html', ranges=query_db("SELECT * FROM ranges"))



@bp.route('/calendar', methods=["POST", "GET"])
@login_required
def planner():
    business_hours = [
        #specify an array instead
        {
            "daysOfWeek": [ 1, 2, 3 ], # Monday, Tuesday, Wednesday
            "startTime": '09:00', # 8am
            "endTime": '21:00' # 6pm
        },
        {
            "daysOfWeek": [ 4, 5 ], # Thursday, Friday
            "startTime": '09:00', # 10am
            "endTime": '21:00' # 4pm
        }
    ]
    # print(g.user['id'])
    users = query_db("SELECT first_name, surname FROM user", [])

    if "range" in request.args:
        range = query_db("SELECT * FROM ranges WHERE distance=?", [request.args['range']], one=True)

    if request.method == "POST":
        print('Creating booking')
        user_query = query_db("SELECT first_name, surname FROM user WHERE id=?", [session['user_id']], one=True)
        if request.form['action'] == 'new':

            print(request.form)

            if '+' in request.form['startTime']:
                start_str = request.form['startTime'].split('+')[0]
            elif '.' in request.form['startTime']:
                start_str = request.form['startTime'].split('.')[0]
            else:
                start_str = request.form['startTime']
            if '+' in request.form['endTime']:
                end_str = request.form['endTime'].split('+')[0]
            elif '.' in request.form['endTime']:
                end_str = request.form['endTime'].split('.')[0]
            else:
                end_str = request.form['endTime']

            start_dt = parse(start_str)
            end_dt = parse(end_str)

            # armory_access = request.form['armoryAccess']

            query = "INSERT INTO booking (range, title, user_id, start_time, end_time, allDay, armory_access) VALUES " \
                    "(?, ?, ?, ?, ?, ?, ?)"
            params = [
                request.args["range"],
                " ".join([request.form["bookingFor"],request.args["range"], "Range booking"]),
                g.user['id'],
                start_dt,
                end_dt,
                0,
                0,
            ]
        else:
            print('Deleting Event ID: ' + request.form['eventId'])
            query = "DELETE FROM booking WHERE id = ?"
            params = [
                request.form['eventId']
            ]


        db = get_db()
        db.execute(query, params)
        db.commit()
        db.close()

    return render_template('booking/calendar.html', business_hours=business_hours, range=range, users=users)


@bp.route('get/bookings')
def get_bookings():

    print("Getting Bookings")
    query = "SELECT *, start_time as start, end_time as end FROM booking"
    params = []
    and_required = False

    if request.args.get('start') or request.args.get('end') or request.args.get('range'):
        query = " ".join([query, "WHERE"])

    if request.args.get('range'):
        and_required = True
        query = " ".join([query, "range=?"])
        params.append(request.args['range'])

    if request.args.get('start') and request.args.get('end'):
        start = parse(request.args['start'].split('+')[0])
        end = parse(request.args['end'].split('+')[0])

        if and_required:
            query = " ".join([
            query, "and",
            "start_time BETWEEN ? and ? and end_time BETWEEN ? and ?"])
        else:
            query = " ".join([query,
                "start_time BETWEEN ? and ? and" /
                " end_time BETWEEN ? and ?"])
        params.extend([start, end, start, end])

    print("QUERY", query)
    print("Params", params)
    data = query_db(query, params, dict=True)
    return json.dumps(data, default=default)


@bp.route('check/bookings')
def check_availability():
    range = request.args['range']
    start = parse(request.args['start'].split('+')[0])
    end = parse(request.args['end'].split('+')[0])

    print(request.args['start'].split('+')[0], request.args['end'].split('+')[0])

    query = "SELECT count(*) AS bookings FROM booking WHERE range=? AND start_time BETWEEN ? and ? AND end_time BETWEEN ? and ?"
    params=[range, start, end, start, end]
    # return jsonify( query_db(query, params, one=True)[0] )
    print(json.dumps(
        query_db("SELECT * FROM booking WHERE range=? AND start_time BETWEEN ? and ? AND end_time BETWEEN ? and ?", params, dict=True)
        , default=default
    ))
    return json.dumps( query_db(query, params, dict=True), default=default)

def rreplace(s, old, occurances, new=''):
    li = s.rsplit(old, occurances)
    return new.join(li)

def render_datetime(ts):
    parts = ts.split('T')
    y, m, d = parts[0].split('-')
    h, M, s, ms = parts[1].split(':')
    d = date(int(y), int(m), int(d))
    t = time(int(h), int(M))
    return datetime.combine(d, t)


def default(o):
    if isinstance(o, (date, datetime)):
        return o.strftime("%Y-%m-%dT%H:%M")
    else:
        print(o)
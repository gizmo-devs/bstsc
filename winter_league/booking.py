from datetime import datetime, date, time
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, query_db
from .auth import login_required

bp = Blueprint('booking', __name__, url_prefix='/booking')


@login_required
@bp.route('/')
def index():
    return render_template('booking/index.html', ranges=query_db("SELECT * FROM ranges"))


@login_required
@bp.route('/calendar', methods=["POST", "GET"])
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
    if "range" in request.args:
        print(request.args["range"])

    if request.method == "POST":
        print(request.form)

        start_dt = render_datetime(request.form['startTime'])
        end_dt = render_datetime(request.form['endTime'])
        query = "INSERT INTO booking (range, title, user_id, start_time, end_time, allDay, armory_access) VALUES " \
                "(?, ?, ?, ?, ?, ?, ?)"
        params = [
            request.args["range"],
            " ".join([request.args["range"], "Range booking"]),
            g.user['id'],
            start_dt,
            end_dt,
            0,
            0
        ]
        db = get_db()
        db.execute(query, params)
        db.commit()
        db.close()

    return render_template('booking/calendar.html', business_hours=business_hours)


@bp.route('get/bookings')
def get_bookings():
    print("Getting Bookings")
    if request.args.get('range'):
        data = query_db("SELECT *, start_time as start, end_time as end FROM booking where range=?",[request.args['range']], dict=True)
    else:
        data = query_db("SELECT *, start_time as start, end_time as end FROM booking",
                        [], dict=True)
    return json.dumps(data, default=default)


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
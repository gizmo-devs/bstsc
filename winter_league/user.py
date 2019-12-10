from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import pandas as pd
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db, query_db
from . import team

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/")
def home():
    edit_button = "<button class='btn btn-info'>Edit</button>"
    df = pd.read_sql_query('SELECT id, first_name, surname, permission_level FROM user', get_db())
    df.columns = ['id', 'First Name', 'Surname', 'Permission Level']
    df['Edit'] = edit_button
    return render_template('postal/all_users.html',  tables=[df.to_html(classes='table results user', border=0, index=False, index_names=False, escape=False)], titles=df.columns.values)

@bp.route("/<int:user_id>", methods=['GET', 'POST'])
def specific_user(user_id):
    if request.method == 'GET':
        sql = 'SELECT * FROM user WHERE id = ?'
        user = query_db(sql, [user_id], one=True)

        return render_template('postal/user.html', user_data=user)
    elif request.method == 'POST':
        #id = request.form['u_id']
        first_name = request.form['first_name']
        surname = request.form['surname']
        username = request.form['username']
        sql = 'UPDATE user SET first_name=?, surname=?, username=? WHERE id = ?'
        db = get_db()
        db.execute(sql, [first_name, surname, username, user_id])
        db.commit()
        flash('{} {} has been updated.'.format(first_name, surname))
        return redirect(url_for('user.home'))

@bp.route("/create", methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        #id = request.form['u_id']
        first_name = request.form['first_name']
        surname = request.form['surname']
        username = request.form['username']
        sql = 'INSERT INTO user (first_name, surname, username) VALUES (?,?,?)'
        db = get_db()
        db.execute(sql, [first_name, surname, username])
        db.commit()
        flash('{} {} has been created.'.format(first_name, surname))
        return redirect(url_for('user.home'))
    else:
        return render_template('postal/create_user.html', user_data=None)

@bp.route("/<int:user_id>/stats", methods=['GET', 'POST'])
def user_stats(user_id):
    if request.method == 'GET':
        user_details = query_db('SELECT * FROM user WHERE id = ?', (str(user_id)), one=True)
        return render_template('postal/user_stats.html', user=user_details)


@bp.route("/<int:user_id>/prev_results/<int:rounds>", methods=['GET', 'POST'])
def previous_round_results(user_id, rounds=12):
    data_set = query_db("""
    SELECT 
        result, first_name, surname
    FROM
        scores
        JOIN user ON user.id = scores.user_id
    WHERE user_id = ?
    LIMIT ? 
    """, (user_id, rounds))
    results = []
    for val in data_set:
        results += [val['result']]
    data = {
        'shooter': data_set[0]['first_name'] + " " + data_set[0]['surname'],
        'rounds': [r for r, idx in enumerate(range(len(data_set)), start=1)],
        'results_arr':results
    }
    print(data)
    return data
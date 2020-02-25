from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import pandas as pd
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db, query_db
from . import team

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/")
@login_required
def home():
    edit_button = "<button class='btn btn-info'>Edit</button>"
    df = pd.read_sql_query('SELECT id, first_name, surname, permission_level FROM user', get_db())
    df.columns = ['ID', 'First Name', 'Surname', 'Permission Level']
    df['Edit'] = edit_button
    return render_template('postal/all_users.html',  tables=[df.to_html(classes='table results user', border=0, index=False, index_names=False, escape=False)], titles=df.columns.values)

@bp.route("/<int:user_id>", methods=['GET', 'POST'])
@login_required
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
        permission_level = request.form['permission_level']
        sql = 'UPDATE user SET first_name=?, surname=?, username=?, permission_level=? WHERE id = ?'
        db = get_db()
        db.execute(sql, [first_name, surname, username, permission_level, user_id])
        db.commit()
        flash('{} {} has been updated.'.format(first_name, surname))
        return redirect(url_for('user.home'))

@bp.route("/create", methods=['GET', 'POST'])
@login_required
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
@login_required
def user_stats(user_id):
    sel_options = query_db("""SELECT compTeam.competition_id as id
         , competition_name as name
        FROM teamMembers
            JOIN compTeam 
                ON compTeam.team_id = teamMembers.team_id
            JOIN competitions 
                ON compTeam.competition_id = competitions.id
        WHERE user_id = ?""", [str(user_id)])
    user_details = query_db("SELECT * FROM user WHERE id = ?", [str(user_id)], one=True)
    fixed_avgs = query_db("""
        SELECT 
            (SELECT AVG(result) FROM scores WHERE user_id = ? ORDER BY scores.completed DESC LIMIT 6) AS six_cards,
            (SELECT AVG(result) FROM scores WHERE user_id = ? ORDER BY scores.completed DESC LIMIT 12) AS twelve_cards,
            (SELECT AVG(result) FROM scores WHERE user_id = ? AND completed BETWEEN date('now', '-28 days') AND date('now')) as four_weeks,
            (SELECT AVG(result) FROM scores WHERE user_id = ? AND completed BETWEEN date('now', '-2 months') AND date('now')) as two_months
        """, [str(user_id), str(user_id), str(user_id), str(user_id)], one=True)
    if request.method == 'GET':
        graph_data = previous_round_results(user_id=user_id, rounds=12)
    else:
        comp_id = request.form['sel_stats']
        if comp_id == "0":
            graph_data = previous_round_results(user_id=user_id, rounds=12)
        else:
            graph_data = user_comp_stats(user_id=user_id, comp_id=comp_id)
    return render_template('postal/user_stats.html', user=user_details, avgs=fixed_avgs, user_comps=sel_options, graph_data=graph_data)


@bp.route("/<int:user_id>/prev_results/<int:rounds>", methods=['GET', 'POST'])
@login_required
def previous_round_results(user_id, rounds=12):
    print("user_id", user_id)
    data_set = query_db("""
    SELECT 
        result, first_name, surname
    FROM
        scores
        JOIN user ON user.id = scores.user_id
    WHERE user_id = ?
    --ORDER BY scores.completed DESC 
    LIMIT ? 
    """, (user_id, rounds))
    results = []
    for val in data_set:
        results += [val['result']]
    data = {
        'comp_id': 0,
        'shooter': data_set[0]['first_name'] + " " + data_set[0]['surname'],
        'rounds': [r for r, idx in enumerate(range(len(data_set)), start=1)],
        'results_arr':results,
        'average' : [(sum(results) / len(results)) for avg in range(len(data_set))]
    }
    return data


@bp.route("/<int:user_id>/stats/<int:comp_id>", methods=['GET', 'POST'])
@login_required
def user_comp_stats(user_id, comp_id):
    print("user_id", user_id, "comp_id", comp_id)
    data_set = query_db("""
        SELECT 
            result, first_name, surname
        FROM
            scores
            JOIN user 
                ON user.id = scores.user_id      
            WHERE user_id=? AND competition_id=?
        order by round
        """, (user_id, comp_id))
    results = []
    for val in data_set:
        results += [val['result']]
    data = {
        'comp_id': comp_id,
        'shooter': data_set[0]['first_name'] + " " + data_set[0]['surname'],
        'rounds': [r for r, idx in enumerate(range(len(data_set)), start=1)],
        'results_arr': results,
        'average': [(sum(results) / len(results)) for avg in range(len(data_set))]
    }
    return data
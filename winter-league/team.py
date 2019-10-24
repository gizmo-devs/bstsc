from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import json
from .auth import login_required
from .db import get_db

bp = Blueprint('team', __name__, url_prefix='/teams')


@bp.route('/')
def index():
    db = get_db()
    teams = db.execute(
        'SELECT DISTINCT id, team_name, team_size, season'
        ' FROM team'
    ).fetchall()

    teamData = []

    for team in teams:
        users = db.execute(
            'SELECT user.id, user.first_name, user.surname'
            ' FROM user'
            ' join teamMembers ON user_id=user.id'
            ' AND team_id=' + str(team['id'])
        ).fetchall()
        teaminfo = {
            "details" : team,
            "members" : users
        }
        teamData.append(teaminfo)
    print("PRINTING TEAM DATA")
    print (teamData)

    users = db.execute(
        'SELECT user.id, user.first_name, user.surname'
        ' FROM user'
        ' join teamMembers ON user_id=user.id'
    ).fetchall()

    return render_template('postal/teams.html', teams=teamData)


@bp.route('/create' , methods=('GET', 'POST'))
def team_create():
    db = get_db()
    users = db.execute('SELECT id, first_name, surname FROM user').fetchall()
    db.commit()
    if request.method == 'POST':
        print("Creating Team")
        team_name = request.form['team_name']
        team_size = request.form['team_size']
        season = request.form.get('season')

        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO team (team_name, team_size, season) VALUES (?, ?, ?)',
            (team_name, team_size, season)
        ).fetchall()

        team_id = cursor.lastrowid

        print("Assigning members to the team : " + str(team_id))
        for member in request.form.getlist("member_selection"):
            #print member
            db.execute(
                'INSERT INTO teamMembers (user_id, team_id) VALUES (?, ?)',
                (member, team_id)
            ).fetchall()
            db.commit()

    return render_template('postal/manage_team.html', users=users)

@bp.route('/edit/<int:id>' , methods=('GET', 'POST'))
def team_edit(id):
    db = get_db()
    users = db.execute('SELECT id, first_name, surname FROM user').fetchall()
    db.commit()
    if request.method == 'POST':
        print("Editing Team")
        team_name = request.form['team_name']
        team_size = request.form['team_size']
        season = request.form['season']

        cursor = db.cursor()
        cursor.execute(
            'UPDATE team'
            ' SET team_name = ?'
            ', team_size = ?'
            ', season = ?'
            ' WHERE id=?', (team_name, team_size, season, id)
        )
        db.commit()
        return redirect(url_for('team.index'))
    elif request.method == 'GET':
        team_details = db.execute(
            'SELECT user.id, user.first_name, user.surname, team.team_name, team.team_size, team.season, team.id as team_id'
            ' FROM user'
            ' join teamMembers ON user_id=user.id'
            ' join team on teamMembers.team_id = team.id'
            ' AND teamMembers.team_id=' + str(id)
        ).fetchall()
    return render_template('postal/edit_team.html', team_details=team_details, users=users)

# @bp.route('/del')
# def team_del():
#     db = get_db()
#     db.execute(
#         'DELETE FROM team WHERE id = 1'
#     )
#     db.commit()
#
#     return render_template('postal/manage_team.html')

def get_team(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/edit/<int:tid>/remove_member/<int:uid>', methods=('GET', 'POST'))
def remove_member(uid, tid):
    db = get_db()
    db.execute(
            'DELETE FROM teamMembers WHERE user_id=? AND team_id=?', (uid, tid)
        )
    db.commit()
    return redirect(url_for('team.team_edit', id=tid))


@bp.route('/edit/<int:tid>/add_member', methods=('GET', 'POST'))
def add_member(tid):
    uid = request.form['member_selection']
    db = get_db()
    db.execute(
            'INSERT INTO teamMembers (user_id, team_id) VALUES(?, ?)', (uid, tid)
        )
    db.commit()
    return redirect(url_for('team.team_edit', id=tid))

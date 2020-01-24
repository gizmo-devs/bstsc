from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import json
from .auth import login_required
from .db import get_db, query_db

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
        users = query_db(
            'SELECT user.id, user.first_name, user.surname, teamMembers.submitted_avg'
            ' FROM user'
            ' join teamMembers ON user_id=user.id'
            ' AND team_id=?', [str(team['id'])])
        active_comps = query_db(
            'SELECT competition_name FROM competitions WHERE id IN '
            '(SELECT competition_id FROM compTeam WHERE team_id=?)', str(team['id'])
        )
        avgs = query_db("""SELECT printf("%.1f", avg(result)) as curr_avg, user_id, competition_id FROM scores
        group by user_id
        having user_id in (select user_id from teamMembers where team_id=?);""", [team['id']])

        teaminfo = {
            "details" : team,
            "avgs" : avgs,
            "active_comps" : active_comps,
            "members" : users
        }
        teamData.append(teaminfo)
    #print("PRINTING TEAM DATA")
    #print (teamData)

    return render_template('postal/teams.html', teams=teamData)


@bp.route('/create', methods=('GET', 'POST'))
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
        )
        db.commit()

        team_id = cursor.lastrowid
        print("new team id", team_id)
        return redirect(url_for('team.team_edit', id=team_id))

    return render_template('postal/create_team.html', users=users)

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
            'SELECT '
            'team.id as team_id'
            ', team.team_name'
            ', team.team_size'
            ', team.season '
            ', teamMembers.id as tm_id'
            ', teamMembers.user_id'
            ', teamMembers.team_id'
            ', teamMembers.submitted_avg'
            ', user.id'
            ', user.first_name'
            ', user.surname '
            'FROM team'
            ' left join teamMembers '
            ' on team.id = teamMembers.team_id'
            ' left join user' 
            ' on teamMembers.user_id = user.id'
            ' WHERE team.id =' + str(id)
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

@bp.route("get_team/<int:id>")
def get_team(id):
    active_comps = query_db(
        'SELECT competition_name FROM competitions WHERE id IN '
        '(SELECT competition_id FROM compTeam WHERE team_id=?)', str(id)
    )
    members = get_members(id)

    # if post is None:
    #     abort(404, "Post id {0} doesn't exist.".format(id))
    #
    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    print("Active Comps : ", active_comps)
    print(members)
    return "Done"


@bp.route('/link/<int:team_id>', methods=('GET', 'POST'))
def link_to_comp(team_id):
    if request.method == 'POST':
        print("You have tried to link a competiton")
        comp_id = request.form['linked_comp']
        db = get_db()
        db.execute(
            'INSERT INTO compTeam (team_id, competition_id) VALUES (?,?)', (str(team_id), str(comp_id))
        )
        db.commit()
        return redirect(url_for('team.index'))
    else:

        team = query_db(
                'SELECT id, team_name FROM team WHERE id=?', str(team_id), one=True
            )
        print (team)
        comps = query_db(
                'SELECT * FROM competitions'
            )

    return render_template('postal/link_team.html', competitions=comps, team=team)


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
    avg = request.form['sub_avg']
    db = get_db()
    db.execute(
            'INSERT INTO teamMembers (user_id, team_id, submitted_avg) VALUES(?, ?, ?)', (uid, tid, avg)
        )
    db.commit()
    return redirect(url_for('team.team_edit', id=tid))


@bp.route('/edit/<int:tid>/avg_ud/<int:tm_id>', methods=['GET'])
def member_avg_ud(tid, tm_id):
    avg = request.args.get('avg');
    db = get_db()
    db.execute(
            'UPDATE teamMembers SET submitted_avg=? WHERE id=?', (avg, tm_id)
        )
    db.commit()
    return '{ status : success}'


def get_members(team_id):
    query = 'SELECT '\
    'teamMembers.*, user.first_name, user.surname '\
    'FROM teamMembers '\
    'JOIN user'\
    '    ON teamMembers.user_id = user.id '\
    'WHERE team_id = ?'

    return query_db(query, str(team_id))


    # db = get_db()
    # team = db.execute(
    #     'SELECT '
    #     'teamMembers. *, user.first_name, user.surname '
    #     'FROM '
    #     'teamMembers '
    #     'JOIN user'
    #     '    ON teamMembers.user_id = user.id '
    #     'WHERE team_id = ?', str(team_id)
    # ).fetchall()
    #
    # cur = get_db().execute(query, args)
    # rv = cur.fetchall()
    # cur.close()
    # tpl = team
    # print (tpl, type(tpl))
    # return (tpl)
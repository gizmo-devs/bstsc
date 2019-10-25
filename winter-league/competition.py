from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import os, json
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import team

bp = Blueprint('competition', __name__, )


@bp.route('/')
def index():
    # db = get_db()
    # comps = db.execute(
    #     'SELECT '
    #         'teamMembers.team_id, '
    #         'user.first_name, '
    #         'user.surname, '
    #         'compTeam.competition_id, '
    #         'scores.round, '
    #         'scores.estimated, '
    #         'scores.completed, '
    #         'competitions.* '
    #     'FROM teamMembers '
    #     'JOIN user ON (teamMembers.user_id = user.id) '
    #     'join compTeam On (compTeam.team_id = teamMembers.team_id) '
    #     'JOIN scores ON (user.id = scores.user_id AND compTeam.competition_id = scores.competition_id) '
    #     'JOIN competitions ON (compTeam.competition_id = competitions.id) '
    #     'WHERE teamMembers.team_id = 1'
    # ).fetchall()
    # users = db.execute('SELECT id, first_name, surname FROM user').fetchall()
    # SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(SITE_ROOT, 'data_files', 'comp_data.json')
    # print(os.path.exists(json_url))
    # with open(json_url, 'r') as f:
    #     comp_data = json.load(f)
    # print (type(comp_data))
    comp_data=collect_competion_data()
    return render_template('postal/index.html', data=comp_data) #, competitions=comps, users=users)


@bp.route('/competition/create' , methods=('GET', 'POST'))
def comp_create():
    if request.method == 'POST':
        print("You have attempted to create a competition")
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = request.form['rounds']

        db = get_db()
        db.execute(
            'INSERT INTO competitions (competition_name, season, rounds) VALUES (?, ?, ?)',
            (competition_name, season, rounds)
        )
        db.commit()

    return render_template('postal/create_comp.html')


@bp.route('/competition/link/<int:id>' , methods=('GET', 'POST'))
def comp_link(id=None):
    print (id)
    db = get_db()
    if request.method == 'POST':
        print("You have attempted to update a Competition")
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = request.form['rounds']

        db.execute(
            'INSERT INTO compTeam(competition_name, season, rounds) VALUES (?, ?, ?)',
            (competition_name, season, rounds)
        )
        db.commit()
    elif request.method == 'GET':
        compdata = db.execute('SELECT * '
                              ' FROM competitions'
                              ' WHERE id = ?'
                              , str(id)
                              ).fetchone()
        print (compdata)
    return render_template('postal/link_comp.html', data=compdata)



@bp.route('/competition/edit/<int:id>' , methods=('GET', 'POST'))
def comp_edit(id=None):
    db = get_db()
    if request.method == 'POST':
        print("You have attempted to Update a competition", id)
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = int(request.form['rounds'])

        due_list = []

        for round in range(rounds):
            r_due = 'round'+ str(round+1) +'_due'
            if request.form.get(r_due) not in ["", "None", None]:
                due_list += [r_due + " = '" + request.form.get(r_due) + "'"]
        due =", "
        sql_rounds = due.join(due_list)

        sql_beginning = 'UPDATE competitions SET competition_name =?, season =?, rounds =?, '
        sql_where = ' WHERE id = ?'

        sql = sql_beginning + sql_rounds + sql_where
        #print (sql)
        db.execute(sql, (competition_name, season, rounds, id)
        )
        db.commit()
        return redirect(url_for('competition.index'))

    if request.method == "GET":
        comp_details = db.execute(
            'SELECT * '
              ' FROM competitions'
              ' WHERE id = ?'
              , str(id)
              ).fetchone()

        return render_template('postal/edit_comp.html', data=comp_details)
    return render_template('postal/index.html')


@bp.route("/test")
def collect_competion_data():
    db = get_db()
    competitions = {}
    info = db.execute(
        'SELECT * from competitions'
    ).fetchall()
    comp_list = []
    #dict['info'] = info
    for comp in info:
        dict = {}
        dict['info']={}
        due_date_list=[]
        for col in comp.keys():
            i = comp.keys().index(col)
            if col == "id":
                dict['info']["id"] = comp[i]
            if col == "competition_name":
                dict['info']["name"] = comp[i]
            if col == "season":
                dict['info']['season'] = comp[i]
            if col == "rounds":
                dict['info']['rounds'] = comp[i]
            if col.endswith("_due"):
                if comp[i] is not None: due_date_list += [comp[i]]
        if len(due_date_list) > 0:
            dict['round_due_dates'] = due_date_list
        print (due_date_list)
        dict['team_results'] = collect_scores(comp['id'])
        comp_list += [dict]
        del dict
    competitions.update({'competitions': comp_list})

    print(comp_list)

    return competitions

@bp.route("/test/compdata")
def collect_competitors_data():
    competition_id = 1
    db = get_db()
    data = db.execute(
        'SELECT competitions.id'
        ', compTeam.team_id'
        ', teamMembers.user_id'
        ', user.first_name'
        ', user.surname'
        ', scores.round'
        ', scores.estimated'
        ', scores.result'
        ' FROM competitions'
        ' join compTeam on competitions.id = compTeam.competition_id'
        ' join teamMembers on compTeam.team_id = teamMembers.team_id'
        ' join user on teamMembers.user_id = user.id'
        ' join scores on teamMembers.user_id = scores.user_id AND compTeam.competition_id = scores.competition_id'
        ' WHERE scores.competition_id=?', str(competition_id)
    ).fetchall()

    competitors = {}
    print (data)
    for row in data:
        if row['user_id'] not in competitors:
            competitors[row['user_id']] = {"name":row['first_name'] + " "+ row['surname'] }

    print (competitors)
    comp_results = {}
    comp_member = {}
    for shooter in competitors:
        print (shooter)
        scores = []
        for row in data:
            if shooter == row['user_id']:
                scores += [{ 'round' : row['round'], 'est' : row['estimated'], 'actual' : row['result']}]
        # name = result['first_name'].encode()
                competitors[shooter].update({"scores" : scores})
    #print(comp_member)
    print (competitors)
    # comp_results = {}
    # comp_member = {}
    # scores = []
    # for result in data:
    #     scores += [{ 'round' : result['round'], 'est' : result['estimated'], 'actual' : result['result']}]
    #     name = result['first_name'].encode()
    #     comp_member.update({"scores" : scores})
    # print(comp_member)
    return "done"


@bp.route("/test/user_scores")
def collect_scores(comp_id):
    # comp_id are params
    team_results = []
    for member in team.get_members(comp_id):
        member_results = {}
        print(member)
        member_id = member['user_id']
        member_results['user_id'] = member_id
        member_results['name'] = member['first_name'] + ' ' + member['surname']
        db = get_db()
        shooter_results = db.execute(
            'SELECT competitions.id '
            ', compTeam.team_id '
            ', teamMembers.user_id'
            ', user.first_name'
            ', user.surname'
            ', scores.id as score_id'
            ', scores.round'
            ', scores.estimated'
            ', scores.result'
            ' FROM competitions'
            ' join compTeam on competitions.id = compTeam.competition_id'
            ' join teamMembers on compTeam.team_id = teamMembers.team_id'
            ' join user on teamMembers.user_id = user.id'
            ' join scores on teamMembers.user_id = scores.user_id AND compTeam.competition_id = scores.competition_id'
            ' WHERE scores.competition_id=?' 
            ' AND teamMembers.user_id = ?', (comp_id, member_id)
        ).fetchall()
        #print(shooter_results)
        scores = []
        for row in shooter_results:
            scores += [{ 'score_id' : row['score_id'], 'round' : row['round'], 'est' : row['estimated'], 'actual' : row['result']}]
        member_results['scores'] = scores
        # print (member_results)
        team_results += [member_results]
    print team_results
    return team_results
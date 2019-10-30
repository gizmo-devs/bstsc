from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import os, json
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db, query_db
import team

bp = Blueprint('competition', __name__, )


@bp.route('/')
def index():
    # SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(SITE_ROOT, 'data_files', 'comp_data.json')
    # print(os.path.exists(json_url))
    # with open(json_url, 'r') as f:
    #     comp_data = json.load(f)
    # print (type(comp_data))
    comp_data = collect_competion_data()
    return render_template('postal/index.html', data=comp_data)


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


@bp.route('/competition/link/<int:id>', methods=('GET', 'POST'))
def comp_link(id=None):
    print (id)
    db = get_db()
    if request.method == 'POST':
        print("You have attempted to Link a team to a Competition")
        linked_team_id = request.form['linked_team']

        print ("comp ID = ", id, " linking to team_id=", linked_team_id)
        db.execute(
            'INSERT INTO compTeam (team_id, competition_id) VALUES (?, ?)',
            (linked_team_id, id)
        )
        db.commit()
        return redirect(url_for('team.index'))
    elif request.method == 'GET':
        # teams = db.execute(
        #     'SELECT * '
        #     ' FROM team'
        #     ' WHERE id NOT IN (SELECT team_id FROM compTeam)'
        #   ).fetchall()
        comps = db.execute(
            'SELECT * FROM competitions '
            'WHERE id NOT IN (SELECT competition_id FROM compTeam)'
        )
        compdata = db.execute('SELECT * '
                              ' FROM competitions'
                              ' WHERE id = ?'
                              , str(id)
                              ).fetchone()
        print (compdata)
    return render_template('postal/link_comp.html', data=compdata, teams=teams)



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
    return "done"


@bp.route("/test/user_scores")
def collect_scores(comp_id):
    # comp_id are params
    #comp_id =1
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

@bp.route("/round_result/save", methods=["POST"])
def result_save():
    if request.method == 'POST':
        db = get_db()
        print('you have tried to save a result')
        score_id = request.form['score_id']
        comp_id = request.form['competition_id']
        user_id = request.form['user_id']

        est = request.form['estimated']
        res = request.form['actual']
        completed = request.form['date_shot']
        round = request.form['round']
        if request.form['score_id'] in [None, "", 0]:
            sql = "INSERT INTO scores (user_id, competition_id, completed, estimated, result, round) VALUES (?,?,?,?,?,?)"
            params = (user_id, comp_id, completed, est, res, round)
        else:
            sql = "UPDATE scores SET user_id=?, competition_id=?, completed=?, estimated=?, result=?, round=? WHERE id=?"
            params = (user_id, comp_id, completed, est, res, round, score_id)


        print(sql, params)
        db.execute(sql, params)
        db.commit()
        flash("Record added to the Database")
        return redirect(url_for('competition.index'))

@bp.route("/round_result/<int:id>", methods=['GET'])
def result(id=0):
    if request.method == 'GET':
        print(id)
        record_data = query_db(
            'SELECT user_id, competition_id, completed, estimated, result, round '
            'FROM scores '
            'WHERE id = ?', str(id), one=True
        )
        if record_data is not None:
            print (record_data, type(record_data))
            res_dict = {
                "user_id": record_data['user_id'],
                "competition_id": record_data['competition_id'],
                "completed": record_data['completed'],
                "estimated": record_data['estimated'],
                "result": record_data['result'],
                "round": record_data['round']
            }
        return res_dict
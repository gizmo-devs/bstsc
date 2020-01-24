from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import os, json, datetime
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db, query_db
from . import team


bp = Blueprint('competition', __name__, )

today = datetime.datetime.today().date()

@bp.route('/')
def index():
    # SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(SITE_ROOT, 'data_files', 'comp_data.json')
    # print(os.path.exists(json_url))
    # with open(json_url, 'r') as f:
    #     comp_data = json.load(f)
    print ('Requesting competition data')
    comp_data = collect_competion_data()
    return render_template('postal/index.html', data=comp_data, date=today)


@bp.route('/competition/create', methods=('GET', 'POST'))
def comp_create():
    if request.method == 'POST':
        print("You have attempted to create a competition")
        competition_name = request.form['competition_name']
        season = request.form['season']

        db = get_db()
        db.execute(
            'INSERT INTO competitions (competition_name, season) VALUES (?, ?)',
            (competition_name, season)
        )
        db.commit()

        comp_id = query_db('SELECT last_insert_rowid() from competitions', (), one=True)
        return redirect(url_for('competition.comp_edit', comp_id=comp_id[0]))

    return render_template('postal/create_comp.html')


@bp.route('/competition/link/<int:id>', methods=('GET', 'POST'))
def comp_link(id=None):
    #print (id)
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
        print ('Fetching competition details for comp id : ' + str(id))
        compdata = db.execute('SELECT * '
                              ' FROM competitions'
                              ' WHERE id = ?'
                              , str(id)
                              ).fetchone()

    return render_template('postal/link_comp.html', data=compdata, teams=teams)


@bp.route('/competition/edit/<int:comp_id>', methods=('GET', 'POST'))
def comp_edit(comp_id=None):
    db = get_db()
    if request.method == 'POST':
        print("You have attempted to Update a competition", comp_id)
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = int(request.form['rounds'])

        due_list = []

        for round in range(rounds):
            r_due = 'round'+ str(round+1) +'_due'
            if request.form.get(r_due) not in ["", "None", None]:
                due_list += [r_due + "='" + request.form.get(r_due) + "'"]
        due =", "
        sql_rounds = due.join(due_list)

        sql_beginning = 'UPDATE competitions SET competition_name =?, season =?, rounds =?, '
        sql_where = ' WHERE id = ?'

        sql = sql_beginning + sql_rounds + sql_where
        print (sql, competition_name, season, rounds, comp_id)
        db.execute(sql, (competition_name, season, rounds, comp_id)
        )
        db.commit()
        return redirect(url_for('competition.index'))

    if request.method == "GET":

        comp_details = db.execute(
            'SELECT competitions.*'
            ' FROM competitions'
            ' WHERE id = ?'
            , str(comp_id)
        ).fetchone()

        comp_rounds = query_db("SELECT id, num, due_date FROM rounds WHERE comp_id=?", [comp_id])
        print (comp_rounds)
        return render_template('postal/edit_comp.html', data=comp_details, rounds=comp_rounds)
    return render_template('postal/index.html')


@bp.route('/competition/edit/<int:comp_id>/remove_round/<int:round_id>', methods=('GET', 'POST'))
def remove_round(comp_id, round_id):
    db = get_db()
    db.execute(
            'DELETE FROM rounds WHERE comp_id=? AND id=?', (comp_id, round_id)
        )
    db.commit()
    return redirect(url_for('competition.comp_edit', comp_id=comp_id))


@bp.route('/competition/edit/<int:comp_id>/add_round', methods=('GET', 'POST'))
def add_round(comp_id):
    round_num = request.form['new_round_num']
    round_due_date = request.form['round_due_date']
    db = get_db()
    db.execute(
            'INSERT INTO rounds (comp_id, num, due_date) VALUES(?, ?, ?)', (comp_id, round_num, round_due_date)
        )
    db.commit()
    return redirect(url_for('competition.comp_edit', comp_id=comp_id))


@bp.route("/data")
def collect_competion_data():
    db = get_db()
    competitions = {}
    info = query_db(
        'SELECT * from competitions',[]
    )
    comp_list = []
    #dict['info'] = info
    for comp in info:
        dict = {}
        dict['info'] = {}
        due_date_list = []
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
            #if col.endswith("_due"):
            #    if comp[i] is not None: due_date_list += [comp[i]]
        #if len(due_date_list) > 0:
        dict['round_due_dates'] = [round[1] for round in get_comp_due_dates(comp['id'])]
        dict['teams'] = collect_scores(comp['id'])
        comp_list += [dict]
        del dict
    competitions.update({'competitions': comp_list})

    #print(comp_list)

    return competitions

@bp.route("/data/compdata")
def collect_competitors_data():
    competition_id = 1
    db = get_db()
    data = query_db(
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
        ' WHERE scores.competition_id=?', [str(competition_id)]
    )

    competitors = {}
    # print (data)
    for row in data:
        if row['user_id'] not in competitors:
            competitors[row['user_id']] = {"name":row['first_name'] + " "+ row['surname'] }

    # print (competitors)
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
    # print (competitors)
    return jsonify(competitors)


@bp.route("/data/user_scores/<comp_id>")
def collect_scores(comp_id):
    # comp_id are params
    #comp_id = 1
    comp_results = []
    for t in get_competition_teams(comp_id):
        #print("Team ID", t)
        current_team = {}
        current_team.update({'team_id': t['team_id'], "u_team_id": t['compTeam_id'], "team_name": t['team_name'], "shooters": {}})
        team_results = []
        for team_member in team.get_members(t['team_id']):
            #print(team_member)
            member_results = {}
            member_results['user_id'] = team_member['user_id']
            member_results['name'] = team_member['first_name'] + ' ' + team_member['surname']
            shooter_results = get_compeitors_scores(comp_id, team_member['user_id'], t['team_id'])
            scores = []
            for row in shooter_results:
                scores += [{
                    'score_id' : row['score_id'],
                    'round' : int(row['round'] or 0),
                    'est' : int(row['estimated'] or 0),
                    'actual' : int(row['result'] or 0)
                }]
            member_results['scores'] = scores
            team_results += [member_results]

        current_team["shooters"] = team_results
        comp_results += [current_team]
    return comp_results


@bp.route("/data/comp_teams/<comp_id>")
def get_competition_teams(comp_id):
    teams_in_comp = query_db(
        'SELECT compTeam.id as compTeam_id, team_id, team_name from compTeam '
        ' JOIN team ON team.id = compTeam.team_id'
        ' WHERE compTeam.competition_id=?', str(comp_id)
    )
    return teams_in_comp


def get_compeitors_scores(comp_id, user_id, team_id):
    user_results = query_db(
        """
        SELECT 
-- rounds
rounds.comp_id
, rounds.num
-- compTeam
, compTeam.team_id
, compTeam.competition_id
-- teamMembers
, teamMembers.user_id
-- Scores
, scores.id as score_id
, scores.round
, scores.estimated
, scores.result
, scores.completed
, scores.compTeam_id
FROM rounds
LEFT JOIN compTeam 
    ON compTeam.competition_id = rounds.comp_id
LEFT JOIN teamMembers
    ON teamMembers.team_id = compTeam.team_id
LEFT JOIN scores
    ON scores.competition_id = rounds.comp_id
    AND scores.compTeam_id = compTeam.id
        AND teamMembers.user_id = scores.user_id
        AND rounds.num = scores.round
WHERE 
    rounds.comp_id=?
        AND teamMembers.user_id=?
        AND teamMembers.team_id=?;
        """, [comp_id, user_id, team_id]
    )
    return user_results


@bp.route("/<int:comp_id>/due_dates", methods=["GET"])
def get_comp_due_dates(comp_id):
    return query_db(
        "SELECT num, due_date FROM rounds WHERE comp_id = ?"
        , str(comp_id)
    )


@bp.route("/round_result/save", methods=["POST"])
def result_save():
    if request.method == 'POST':
        db = get_db()
        print('You have tried to save a result')
        score_id = request.form['score_id']
        comp_id = request.form['competition_id']
        user_id = request.form['user_id']
        compTeam_id = request.form['compTeam_id']

        est = request.form['estimated']
        res = request.form['actual']
        completed = request.form['date_shot']
        round = request.form['round']
        if request.form['score_id'] in [None, "", 0]:
            sql = "INSERT INTO scores (user_id, competition_id, completed, estimated, result, round, compTeam_id) VALUES (?,?,?,?,?,?,?)"
            params = (user_id, comp_id, completed, est, res, round, compTeam_id)
        else:
            sql = "UPDATE scores SET user_id=?, competition_id=?, completed=?, estimated=?, result=?, round=?, compTeam_id=? WHERE id=?"
            params = (user_id, comp_id, completed, est, res, round, score_id, compTeam_id)


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
            'SELECT user_id, competition_id, completed, estimated, result, round, compTeam_id '
            'FROM scores '
            'WHERE id = ?', [str(id)], one=True
        )
        if record_data is not None:
            print (record_data, type(record_data))
            res_dict = {
                "user_id": record_data['user_id'],
                "competition_id": record_data['competition_id'],
                "completed": record_data['completed'],
                "estimated": record_data['estimated'],
                "result": record_data['result'],
                "round": record_data['round'],
                "compTeam_id" : record_data['compTeam_id']
            }
        return jsonify(res_dict)

@bp.route("/competition/due_dates", methods=['GET', 'POST'])
#@bp.route("/competition/due_dates/<int:comp_id>")
def competition_due_dates():
    comp_details = None
    curr_date = datetime.date.today()
    comps = query_db("SELECT id, competition_name FROM competitions",[])
    if request.method == "POST":
        comp_id = request.form['comp_sel']
        comp_details = query_db("SELECT num, due_date FROM rounds WHERE comp_id=?", [comp_id])

    return render_template('postal/comp_due_dates.html', comp_list=comps, comp_details=comp_details, today=curr_date)



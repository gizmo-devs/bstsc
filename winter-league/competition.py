from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import os, json
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

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
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'data_files', 'comp_data.json')
    print(os.path.exists(json_url))
    with open(json_url, 'r') as f:
        comp_data = json.load(f)
    print (type(comp_data))
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
        rounds = request.form['rounds']

        due = []

        for round in range(int(rounds)):
            r_due = 'round'+ str(round) +'_due'
            if request.form.get(r_due) not in ["", "None", None]:
                due += [request.form.get(r_due)]

        print due
        # round1_due = request.form['round1_due'] if request.form['round1_due'] else 'NULL'
        # round2_due = request.form['round2_due'] if request.form['round2_due'] else 'NULL'
        # round3_due = request.form['round3_due'] if request.form['round3_due'] else 'NULL'
        # round4_due = request.form['round4_due'] if request.form['round4_due'] else 'NULL'
        # round5_due = request.form['round5_due'] if request.form['round5_due'] else 'NULL'
        # round6_due = request.form['round6_due'] if request.form['round6_due'] else 'NULL'
        # round7_due = request.form['round7_due'] if request.form['round7_due'] else 'NULL'
        # round8_due = request.form['round8_due'] if request.form['round8_due'] else 'NULL'
        # round9_due = request.form['round9_due'] if request.form['round9_due'] else 'NULL'
        # round10_due = request.form['round10_due'] if request.form['round10_due'] else 'NULL'
        # round11_due = request.form['round11_due'] if request.form['round11_due'] else 'NULL'
        # round12_due = request.form['round12_due'] if request.form['round12_due'] else 'NULL'
        # round13_due = request.form['round13_due'] if request.form['round13_due'] else 'NULL'
        # round14_due = request.form['round14_due'] if request.form['round14_due'] else 'NULL'
        # round15_due = request.form['round15_due'] if request.form['round15_due'] else 'NULL'
        # round16_due = request.form['round16_due'] if request.form['round16_due'] else 'NULL'
        # round17_due = request.form['round17_due'] if request.form['round17_due'] else 'NULL'
        # round18_due = request.form['round18_due'] if request.form['round18_due'] else 'NULL'
        #
        # print (round5_due)
        # db.execute(
        #     'UPDATE competitions '
        #     'SET competition_name = ' + competition_name +
        #     ', season = ' + season +
        #     ', rounds = ' + rounds +
        #     ', round1_due = ' + round1_due +
        #     ', round2_due = ' + round2_due +
        #     ', round3_due = ' + round3_due +
        #     ', round4_due = ' + round4_due +
        #     ', round5_due = ' + round5_due +
        #     ', round6_due = ' + round6_due +
        #     ', round7_due = ' + round7_due +
        #     ', round8_due = ' + round8_due +
        #     ', round9_due = ' + round9_due +
        #     ', round10_due = ' + round10_due +
        #     ', round11_due = ' + round11_due +
        #     ', round12_due = ' + round12_due +
        #     ', round13_due = ' + round13_due +
        #     ', round14_due = ' + round14_due +
        #     ', round15_due = ' + round15_due +
        #     ', round16_due = ' + round16_due +
        #     ', round17_due = ' + round17_due +
        #     ', round18_due = ' + round18_due +
        #     ' WHERE id = '+ str(id)
        # )
        # db.commit()
        # return render_template('postal/index.html')

    if request.method == "GET":
        comp_details = db.execute(
            'SELECT * '
              ' FROM competitions'
              ' WHERE id = ?'
              , str(id)
              ).fetchone()

        return render_template('postal/edit_comp.html', data=comp_details)
    return render_template('postal/index.html')


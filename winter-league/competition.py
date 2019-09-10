from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('competition', __name__, )


@bp.route('/')
def index():
    db = get_db()
    comps = db.execute(
        'SELECT competition_name, season, rounds, round1_due'
        ' FROM competitions'
    ).fetchall()
    users = db.execute('SELECT id, first_name, surname FROM user').fetchall()
    return render_template('postal/index.html', competitions=comps, users=users)


@bp.route('/create' , methods=('GET', 'POST'))
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


@bp.route('/edit/<int:id>' , methods=('GET', 'POST'))
def comp_link():
    if request.method == 'POST':
        print("You have attempted to update a Competition")
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = request.form['rounds']

        db = get_db()
        db.execute(
            'INSERT INTO compTeam(competition_name, season, rounds) VALUES (?, ?, ?)',
            (competition_name, season, rounds)
        )
        db.commit()
    #elif request.method == 'GET':

    return render_template('postal/create_comp.html')


@bp.route('/edit' , methods=('GET', 'POST'))
def comp_edit():
    if request.method == 'POST':
        print("You have attempted to create a competition")
        competition_name = request.form['competition_name']
        season = request.form['season']
        rounds = request.form['rounds']

        db = get_db()
        db.execute(
            'INSERT INTO compTeam(competition_name, season, rounds) VALUES (?, ?, ?)',
            (competition_name, season, rounds)
        )
        db.commit()

    return render_template('postal/create_comp.html')


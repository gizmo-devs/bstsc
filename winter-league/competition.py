from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('competition', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('postal/index.html', posts=posts)

@bp.route('/create' , methods=('GET', 'POST'))
def comp_create():
    if request.method == 'POST':
        competion_name = request.form['competition_name']
        season = request.form['season']
        rounds = request.form['rounds']

        db = get_db()
        db.execute(
            'INSERT INTO competitions (competion_name, season, rounds) VALUES (?, ?, ?)',
            (competion_name, season,rounds)
        )
        print("You have attempted to create a competition")

    return render_template('postal/create_comp.html')

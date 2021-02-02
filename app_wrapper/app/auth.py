import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    feedback = []
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        # password = request.form['password']
        firstname = request.form['firstname']
        surname = request.form['surname']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
            feedback.append('username')
        # elif not password:
        #     error = 'Password is required.'
        #     feedback.append('password')
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
            feedback.append('username')

        if error is None:
            # db.execute(
            #     'INSERT INTO user (first_name, surname, username, password) VALUES (?, ?, ?, ?)',
            #     (firstname, surname, username, generate_password_hash(password))
            # )
            db.execute(
                'INSERT INTO user (first_name, surname, username, permission_level) VALUES (?, ?, ?, ?)',
                (firstname, surname, username, 'user')
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html', feedback=feedback)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    feedback = []
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        # password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Username "{}" is not recognised.'.format(username)
            feedback.append('username')
        elif not user['permission_level'] == 'user':
            return redirect(url_for('.admin_login', u=username))
        # elif not check_password_hash(user['password'], password):
        #     error = 'Incorrect password.'
        #     feedback.append('password')
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', feedback=feedback)

@bp.route('/login-admin', methods=('GET', 'POST'))
def admin_login():
    feedback = []
    if request.method == 'POST':
        print(request.form)
        username = request.args.get('u').strip().lower()
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Username "{}" is not recognised.'.format(username)
            feedback.append('username')
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            feedback.append('password')
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login_admin.html', feedback=feedback)

@bp.route('/reset_password', methods=('GET', 'POST'))
def reset_user_pw():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is None:
            error = 'User {} is not registered.'.format(username)

        if error is None:
            db.execute(
                'UPDATE user SET password=? WHERE username=?',
                (generate_password_hash(password),username)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/reset_password.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
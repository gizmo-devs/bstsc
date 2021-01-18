import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

import os.path

def get_db(dict=None):
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        if dict:
            g.db.row_factory = dict_factory
        else:
            g.db.row_factory = sqlite3.Row
    else:
        if g.db.row_factory == sqlite3.Row and dict:
            close_db()
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = dict_factory

    return g.db

def query_db(query, args=(), one=False, dict=None):
    cur = get_db(dict).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_db_load():
    db = get_db()

    with current_app.open_resource('data_load.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_db_manual_update():
    db = get_db()
    if os.path.isfile('db_update.sql'):
        print ("File exist")
    with current_app.open_resource('db_update.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('init-db-load')
@with_appcontext
def init_db_load_command():
    """Clear the existing data and create new tables."""
    init_db_load()
    click.echo('Initialized the user data.')


@click.command('init-db-manual-update')
@with_appcontext
def init_db_manual_update():
    """Force an update to the SQLite Database."""
    init_db_manual_update()
    click.echo('Database updated.')

    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_load_command)
    app.cli.add_command(init_db_manual_update)
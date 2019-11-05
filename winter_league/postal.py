from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    competitions = db.execute(
        'SELECT competition_name FROM competitions'
    ).fetchall()
    return render_template('postal/index.html', competitions=competitions)
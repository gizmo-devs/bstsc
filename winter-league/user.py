from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import pandas as pd
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db, query_db
from . import team

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/")
def home():
    editButton = "<button>Edit</button>"
    df = pd.read_sql_query('SELECT first_name, surname, permission_level FROM user', get_db())
    df.columns = ['First Name', 'Surname', 'Permission Level']
    df['Edit'] = editButton
    return render_template('postal/users.html',  tables=[df.to_html(classes='table user', border=0, index=False, index_names=False, escape=False)], titles=df.columns.values)


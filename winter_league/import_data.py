from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import json, os
from .auth import login_required
from .db import get_db, query_db
from pprint import pprint

bp = Blueprint('import_data', __name__, url_prefix='/import')

@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    List files and give options for each file: Add, Delete, Archive
    :return:
    """
    files = []
    if request.method == 'POST':
        team_id = request.form['chosen_team']
        file = request.form['file']
        print(team_id, file)
        return redirect(url_for('import_data.process_upload', team_id=team_id, file=file))
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    for file in file_list:
        files.insert(0, tuple((file, unix_to_format(os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file)).st_mtime))))

    files.sort(key=takeSecond, reverse=True)

    print(files)
    sql = """SELECT compTeam.id as id
    , competitions.competition_name as comp
    , team.team_name as team_name
    FROM compTeam
    JOIN competitions ON competitions.id = compTeam.competition_id
    JOIN team ON team.id = compTeam.team_id"""
    return render_template('/import/import_index.html', file_list=files, teams=query_db(sql,[]))


@bp.route('/upload', methods=['GET', 'POST'])
def upload_data():
    """
    Upload file to data_files/uploads
    :return:
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        print(file.filename, request.files['file'])
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            print('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('import_data.index'))
        else:
            flash('Incorrect file Extension.')
            return redirect(request.url)

    return render_template('import/import.html',  allow=app.config['ALLOWED_EXTENSIONS'])

def get_club_data(file, club, name=None):
    import pandas as pd
    data = pd.read_excel(open(file, 'rb'), sheet_name='Club Scores', skiprows=1)
    data = data.drop(columns=['Unnamed: 25',"status", "Average", "Average.1", "+/-"])
    return data[data['Club'] == 'Budleigh Salterton'].to_dict('records')


@bp.route('/preview', methods=['GET','POST'])
def compare_data(imported_data, compTeam_id):
    sql = """SELECT team_id, competition_id FROM compTeam WHERE id =?"""
    q = query_db(sql, [compTeam_id], one=True)

    sql = """SELECT 
    compTeam.competition_id
    , teamMembers.user_id
    , user.first_name || ' ' || user.surname as Name
    , scores.id as score_id
    , scores.round
    , scores.estimated
    , scores.result
    , scores.completed
    , scores.compTeam_id
    FROM rounds
    JOIN compTeam 
        ON compTeam.competition_id = rounds.comp_id
    JOIN teamMembers
        ON teamMembers.team_id = compTeam.team_id
    JOIN scores
        ON scores.competition_id = rounds.comp_id
        AND scores.compTeam_id = compTeam.id
            AND teamMembers.user_id = scores.user_id
            AND rounds.num = scores.round
    JOIN user ON user.id = scores.user_id
    WHERE 
        scores.compTeam_id=?
    order by scores.user_id"""

    sql="""SELECT 
    compTeam.competition_id
    , teamMembers.user_id
    , user.first_name || ' ' || user.surname as Name
    , scores.id as score_id
    , rounds.num as round
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
    JOIN user ON user.id = teamMembers.user_id
    WHERE 
        rounds.comp_id=?
            AND teamMembers.team_id=?
    order by teamMembers.user_id;"""
    db_results=query_db(sql, [q['competition_id'], q['team_id']])

    data_dict = dict(data=[])

    for result in db_results:
        round = dict(
            round=result['round'],
            db_result=result['result'],
            score_id=result['score_id'],
            import_score=None
        )

        for d in imported_data:
            if d['Name'].strip() == result['Name'].strip():
                round['import_score'] = int(d['r' + str(result['round'])])

        if result['Name'] not in [shooter['Name'] for shooter in data_dict['data']]:
            print('not found')
            data_dict['data'].append(
                {"Name": result['Name'], 'user_id':result['user_id'], 'comp_id':result['compTeam_id'], 'rounds':[]}
            )

        for d in data_dict['data']:
            if d['Name'] == result['Name']:
                d['rounds'].append(round)

        del(round)
    print(json.dumps(data_dict))
    return data_dict


@bp.route('/process', methods=['GET','POST'])
def process_upload():
    if request.method == 'POST':
        db = get_db()
        score_id = request.form['score_id']
        impoted_score = request.form['Imported']
        print(score_id, impoted_score)
        sql = "UPDATE scores SET result=? WHERE id=?"
        params = (impoted_score, score_id)
        db.execute(sql, params)
        db.commit()

    team_id = request.args.get('team_id')
    filename = request.args.get('file')

    data = get_club_data(file=os.path.join(app.config['UPLOAD_FOLDER'], filename), club='Budleigh Salterton')
    print (json.dumps(data))
    all_data = compare_data(imported_data=data, compTeam_id=team_id)
    return render_template('import/preview_data.html', data=all_data)


# @bp.route('/preview', methods=['GET','POST'])
# def compare_data(imported_data, compTeam_id):
#     db_data = []
#     results= []
#     sql = """SELECT
#         user.first_name || ' ' || user.surname as Name,
#         max(case when round = 1 then result else 0 end) as r1
#         , max(case when round = 2 then result else 0 end) as r2
#         , max(case when round = 3 then result else 0 end) as r3
#         , max(case when round = 4 then result else 0 end) as r4
#         , max(case when round = 5 then result else 0 end) as r5
#         , max(case when round = 6 then result else 0 end) as r6
#         , max(case when round = 7 then result else 0 end) as r7
#         , max(case when round = 8 then result else 0 end) as r8
#         , max(case when round = 9 then result else 0 end) as r9
#         , max(case when round = 10 then result else 0 end) as r10
#         , max(case when round = 11 then result else 0 end) as r11
#         , max(case when round = 12 then result else 0 end) as r12
#         , max(case when round = 13 then result else 0 end) as r13
#         , max(case when round = 14 then result else 0 end) as r14
#         , max(case when round = 15 then result else 0 end) as r15
#         , max(case when round = 16 then result else 0 end) as r16
#         , max(case when round = 17 then result else 0 end) as r17
#         , max(case when round = 18 then result else 0 end) as r18
#     FROM scores
#         JOIN user ON user_id = user.id
#     WHERE
#     compTeam_id = ?
#     GROUP BY user_id
#     ORDER BY user_id;"""
#     db_raw_data = query_db(sql, [ compTeam_id]) #user_id,
#
#     for i in db_raw_data:
#         import_clone = imported_data
#         imported_results = []
#         db_name = i['Name']
#         print("DB_Name", db_name)
#         for record in import_clone:
#             if record.get('Name') is not None and str_cleanse(record.get('Name')) == str_cleanse(db_name):
#                 print("MATCH FOUND")
#                 imported_results = results_to_list(record)
#             else:
#                 print("STRIPPED : ",record.get('Name'))
#
#         db_data.append(
#             {
#                 "Name": i['name'],
#                 "db_results":[i[k] for k in i.keys() if k != 'Name'],
#                 "imported_results": imported_results
#             }
#         )
#     overall_data = {
#         "records": db_data
#     }
#     # data = {
#     #     "db": db_data, "imported": imported_data
#     # }
#     print(json.dumps(overall_data))
#     return overall_data


@bp.route('/uploads/<filename>')
def download_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@bp.route('/uploads/del_file/', methods=['GET', 'POST'])
def delete_file():
    filename = request.form['file']
    print(filename)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except:
        flash("Could not delete '"+filename+"'")
    else:
        flash("File '"+filename+"' Deleted")

    return "File Deleted", 200


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def str_cleanse(s):
    return s.strip() if s is not None else False

def unix_to_format(unix, format='%Y-%m-%d %H:%M:%S'):
    from datetime import datetime
    return datetime.utcfromtimestamp(unix).strftime(format)

def takeSecond(elem):
    return elem[1]


def results_to_list(data_dict):
    # print(data_dict['Name'])
    if data_dict is None:
        print("Nothing sent through")
        return {}

    new_dict = dict(Name=data_dict.pop('Name'))

    for key in ['Cards', 'Club']:
        if key in data_dict:
            del data_dict[key]

    for key in data_dict:
        if key.startswith('r'):
            data_dict[key[1:]] = data_dict.pop(key)

    for key in data_dict:
        data_dict[int(key)] = data_dict.pop(key)

    new_dict["imported_results"] = [int(data_dict[k]) for k in sorted(data_dict)]
    print(new_dict["imported_results"])
    return new_dict["imported_results"]



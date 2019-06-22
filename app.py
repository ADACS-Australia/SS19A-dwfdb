import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Dwf, Post


@app.route("/")
def hello():
    return "Hello World!"

#
# Methods for Mary Runs
#

# Get Run
@app.route('/web/get_run', methods=['GET'])
def get_run():
    app.logger.debug("Fetching run")
    ra = float(request.args['RA'])
    d = float(request.args['d'])
    dec = request.args['DEC']
    con = sqlite3.connect("../instance/adacsdwf.sqlite")
    c = con.cursor()

    # Do some magic
    results = c.execute(
        # 'SELECT * FROM dwf WHERE RA-?<=? AND DEC-?<=?',
        'SELECT RA FROM dwf WHERE ABS(RA-?)<=?', (ra,d)
    ).fetchall()

    if results is None:
        abort(404, "There are no objects found within {0} of RA {0} and DEC {0}.".format(d, ra, dec))

    app.logger.info("[web] get run successfully called")
    return jsonify(results)


# Get all run
@app.route('/web/run/all', methods=['GET'])
def get_run_all():
    con = sqlite3.connect("../instance/adacsdwf.sqlite")
    c = con.cursor()
    results = c.execute("SELECT * FROM dwf").fetchall()

    # results=None
    if results is None:
        r = {"error": 'No data supplied'}
        # abort(404, "There are no posts for mary id {0}.".format(id))
        return jsonify(r)
    else:
        # res_dic=[dict(zip([key[0] for key in c.description],row)) for row in results]
        return jsonify(results)
    # app.logger.info("[web] get run successfully called")


# Get image metadata
@app.route('/web/create', methods=('GET', 'POST'))
def create_run():
    #app.logger.debug("Fetching image")
    # values = {'title': 'jack', 'type': None, 'genre': 'Action', 'onchapter': None, 'chapters': 6, 'status': 'Ongoing'}
    # cur.execute(
    #     'INSERT INTO Media (id, title, type, onchapter, chapters, status) VALUES (:id, :title, :type, :onchapter, :chapters, :status);'), values)

    if request.method == "POST":
        con = sqlite3.connect("../instance/adacsdwf.sqlite")
        c = con.cursor()
        columns = [request.get_json()[k] for k in night_key]

        results = c.execute('SELECT * FROM dwf WHERE (maryID=? OR sci_path=? OR sub_path=? OR temp_path=?)',
                  (request.get_json()['maryID'],request.get_json()['sci_path'],request.get_json()['sub_path'],request.get_json()['temp_path'])).fetchall()
        if not results:

            c.execute('INSERT INTO dwf VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', columns)
            # # c.execute('INSERT INTO dwf (ID, field, ccd, mary_run, date, cand_num, mag, emag, mjd, RA, DEC, maryID, sci_path, sub_path, temp_path) VALUES(:ID, :field, :ccd, :mary_run, :date, :cand_num, :mag, :emag, :mjd, :RA, :DEC, :maryID, :sci_path, :sub_path, :temp_path);', request.get_json())
            con.commit()

            results = c.execute("SELECT * FROM dwf WHERE maryID=?",(request.get_json()['maryID'])).fetchall()
            if not results:
                r = {"error": "data wasn't committed"}
                return jsonify(r)
            else:
                return jsonify(results)
        else:
            r = {"error": 'data already exists use update function instead'}
            return jsonify(r)






#
# Methods for commenting on objects
#

@app.route('/web/posts/create', methods=('GET', 'POST'))
def create_post():
    if request.method == 'POST':
        body = query_parameters.get('body')
        maryid = query_parameters.get('maryID')
        author = query_parameters.get('author')
        error = None

        if body is None:
            r = {"error": 'No comment supplied'}
            # abort(404, "There are no posts for mary id {0}.".format(id))
            return jsonify(r)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (author, body, maryID, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (author, body, maryid, g.user['id'])
            )
            db.commit()
            return jsonify({"request": "successfully received"})

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@app.route('/web/posts', methods=['POST'])
def get_post_api():
    id = query_parameters.get('id')
    post = get_db().execute(
        'SELECT maryID, body, created, author'
        ' FROM post'
        ' WHERE maryID = ?', id
    ).fetchone()

    if post is None:
        r = {"error": 'No posts for this maryID'}
        # abort(404, "There are no posts for mary id {0}.".format(id))
        return jsonify(r)
    else:
        return jsonify(post)


@app.route('/web/posts/<int:id>/update', methods=('GET', 'POST'))
def update_post(id):
    post = get_post(id)

    if request.method == 'POST':
        body = query_parameters.get('body')
        maryid = query_parameters.get('maryID')
        author = query_parameters.get('author')
        error = None

        if not body:
            r = {"error" : 'comment is required.'}


        if error is not None:
            return jsonify(r)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET author = ?, body = ?, maryID = ?'
                ' WHERE id = ?',
                # (body, author, g.dwf['maryID'])
                (body, author, maryid, id)
            )
            db.commit()
    return jsonify(post)


# @app.route("/name/<name>")
# def get_book_name(name):
#     return "name : {}".format(name)
#
# @app.route("/details")
# def get_book_details():
#     author=request.args.get('author')
#     published=request.args.get('published')
#     return "Author : {}, Published: {}".format(author,published)

if __name__ == '__main__':
    app.run()

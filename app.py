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

# Get all candidates within in d degrees of RA and Dec
@app.route('/web/get_run', methods=['GET'])
def get_run():
    app.logger.debug("Fetching run")
    ra = float(request.args['RA'])
    d = float(request.args['d'])
    dec = request.args['DEC']


    results = Dwf.query.filter(abs(Dwf.ra - ra) <= d, abs(Dwf.dec - dec) <= d)

    if results is None:
        r={"error" : "There are no objects found within {0} of RA {0} and DEC {0}.".format(d, ra, dec)}
        return jsonify(r)
    else:
        app.logger.info("[web] get run successfully called")
        return jsonify(results)


# Get all records of candidates
@app.route('/web/run/all', methods=['GET'])
def get_run_all():
    all_records = Dwf.query.all()
    results = [e.serialize() for e in all_records]
    if results is None:
        r = {"error": 'No data supplied'}
        return jsonify(r)
    else:
        return jsonify(results)
    # app.logger.info("[web] get run successfully called")


# save candidate metadata to DB
@app.route('/web/create', methods=('GET', 'POST'))
def create_run():
    #app.logger.debug("Fetching image")

    if request.method == "POST":
        results = User.query.get(request.get_json()['maryID'])

        if not results:
            new_record = Dwf(request.get_json)
            db.session.add(new_record)
            db.session.commit()

            results = User.query.get(request.get_json()['maryID'])
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

        try:
            new_post = Post(body=query_parameters.get('body'),
                            maryid = query_parameters.get('maryID'),
                            author = query_parameters.get('author'))
            db.session.add(new_post)
            db.session.commit()
            r = {"success":"post with maryID={} was added to DB".format(new_post.maryid)}
            return jsonify(r)
        except Exception as e:
            r = {"error":str(e)}
            return jsonify(r)


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

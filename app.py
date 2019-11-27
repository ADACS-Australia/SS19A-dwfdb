import os
from flask import jsonify
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime
from collections import namedtuple

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *


@app.route("/")
def hello():
    return "Hello World!"


#
# Methods for Mary Runs
#

# Get all candidates within in d degrees of RA and Dec
@app.route('/web/run', methods=['GET'])
def get_run():
    #app.logger.debug("Fetching run")
    if request.method == 'GET':
        ra = float(request.get_json()['ra'])
        d = float(request.get_json()['d'])
        dec = float(request.get_json()['dec'])

        query_result = db.session.execute('SELECT * FROM dwf WHERE dwf.ra - :ra < :d AND dwf.dec - :dec < :d',{'ra': ra, 'd': d, 'dec': dec})
        Record = namedtuple('Record', query_result.keys())
        records = [Record(*r) for r in query_result.fetchall()]

        if records is None:
            r = {"error": "There are no objects found within {0} of RA {0} and DEC {0}.".format(d, ra, dec)}
            return jsonify(r)
        else:
            app.logger.info("[web] get run successfully called")
            return jsonify(records)
# raw sql query stackoverflow: https://stackoverflow.com/questions/17972020/how-to-execute-raw-sql-in-flask-sqlalchemy-app

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
@app.route('/web/run/create', methods=['POST'])
def create_run():
    # app.logger.debug("Fetching image")
    #key = ["ID", "field", "ccd", "mary_run", "date", "cand_num", "mag", "emag", 'mjd', "RA", "DEC", "maryID", "sci_path", "sub_path", "temp_path"]

    if request.method == "POST":

        results = Dwf.query.get(request.get_json()['maryID'])

        if not results:
            new_record = Dwf(id=request.get_json()['id'], field=request.get_json()['field'],
                             ccd=request.get_json()['ccd'], mary_run=request.get_json()['mary_run'],
                             date=request.get_json()['date'], cand_num=request.get_json()['cand_num'],
                             mag=request.get_json()['mag'], emag=request.get_json()['emag'],
                             mjd=request.get_json()['mjd'], ra=request.get_json()['ra'], dec=request.get_json()['dec'],
                             maryID=request.get_json()['maryID'], sci_path=request.get_json()['sci_path'],
                             sub_path=request.get_json()['sub_path'], temp_path=request.get_json()['temp_path'])
            db.session.add(new_record)
            db.session.commit()

            records = Dwf.query.filter_by(maryID=request.get_json()['maryID'])
            results = [e.serialize() for e in records]
            if not results:
                r = {"error": "data wasn't committed"}
                return jsonify(r)
            else:
                return jsonify(results)
        else:
            r = {"error": 'data already exists use update_record method instead'}
            return jsonify(r)


# update a mary run entry
@app.route('/web/run/<string:id>/update', methods=['PUT'])
#@app.route('/web/run/update', methods=['PUT'])
def update_run(id):
    if request.method == 'PUT':
        record = Dwf.query.filter(Dwf.maryID == request.get_json()['maryID'])
        # print(record)
        results = [e.serialize() for e in record]
        if not results:
            r = {"error": "no entry found"}
            return jsonify(r)
        else:
            update_record = Dwf.query.filter_by(maryID=id).update(dict(request.get_json()))
            db.session.commit()

            record = Dwf.query.filter(Dwf.maryID == request.get_json()['maryID'])
            results = [e.serialize() for e in record]
            return jsonify(results)


#
# Methods for commenting on objects
#

# save a psot/comment associated with a maryID to the DB
@app.route('/web/post/create', methods=['POST'])
def create_post():
    if request.method == 'POST':

        try:
            new_post = Post(author=request.get_json()['author'],
                            created=datetime.datetime.utcnow(),
                            body=request.get_json()['body'],
                            maryid=request.get_json()['maryid']
                            )
            db.session.add(new_post)
            db.session.commit()
            r = {"success": "post with maryID={} was added to DB".format(new_post.maryid)}
            return jsonify(r)
        except Exception as e:
            r = {"error": str(e)}
            return jsonify(r)



# retrieve all comments associated with a maryID
@app.route('/web/post', methods=['GET'])
def get_post():
    all_records = Post.query.filter_by(maryid=request.get_json()['maryID'])
    results = [e.serialize() for e in all_records]
    if results is None:
        r = {"error": 'No entry found'}
        return jsonify(r)
    else:
        return jsonify(results)


# update a comment based on id (primary key) - no author changes
@app.route('/web/post/<int:id>/update', methods=['PUT'])
def update_post(postid):
    # print(id)
    if request.method == 'PUT':
        post = Post.query.get(postid)
        body = request.get_json()['body']
        author = request.get_json()['author']

        if not post:
            error = {"abort": 'post id is required.'}
            return jsonify(error)
        elif not body:
            error = {"abort": 'post content is required.'}
            return jsonify(error)
        elif author != post.author:
            error = {"abort": 'post author has changed.'}
            return jsonify(error)
        else:
            post.body = "updated: " + body
            post.created = datetime.datetime.utcnow()

            db.session.commit()

            post_update = Post.query.filter_by(id=postid)
            results = [e.serialize() for e in post_update]

            return jsonify(results)


if __name__ == '__main__':
    app.run()

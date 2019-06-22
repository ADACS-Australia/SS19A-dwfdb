import requests
import logging
import numpy as np
from .errors import *
from astropy import units as u
from astropy.coordinates import SkyCoord
#from . import app

# Define a class
class Client(object):
    def __init__(self, api_url=None, sender=None):
        self.api_url = api_url
        self.sender = sender
        # self._xy = None
        self.record = None
        self.point = None
        self.post = None

    def host(self,api_url):
        self.api_url = api_url

    def author(self, sender):
        """set the author/sender of the data packets"""
        self.sender = sender

    #
    # Workflow methods
    #

    def add_record(self, record_dict):
        """creates the dictionary of records and checks data is acceptable"""

        # check if values are validated as per schema (integer and positive)
        for key in ['ID', 'ccd', 'mary_run', 'date', 'cand_num']:
            if type(record_dict.get(key)) is not int:
                raise TableValueError(key + " is not an integer")
            if record_dict.get(key) < 0:
                raise TableValueError(key + " needs to be positive")
            if record_dict.get(key) is None:
                raise TableValueError(key + " is empty")

        # check if required values are numeric
        for key in ['mag', 'emag', 'mjd', 'RA', 'DEC']:
            if type(record_dict.get(key)) is not float:
                raise TableValueError(key + " is not a float")
            if record_dict.get(key) is None:
                raise TableValueError(key + " is empty")

        # check if required values are strings and not NULL
        for key in ['maryID', 'sci_path', 'sub_path', 'temp_path']:
            if type(record_dict.get(key)) is not str:
                raise TableValueError(key + " is not a string")
            if record_dict.get(key) is None:
                raise TableValueError(key + " is empty")

        if not 10.0 <= record_dict['mag'] <= 30.0:
            raise TableValueError("mag is out of bounds")
        if not 0.0 <= record_dict['RA'] <= 360.0:
            raise TableValueError("RA is out of bounds")
        if not -90.0 <= record_dict['DEC'] <= 90.0:
            raise TableValueError("DEC is out of bounds")

        self.record = record_dict

    def add_batch(self, filename):
        """adds content of ascii file of records to the database"""
        f = open(filename, 'r')
        header = f.readline().split()
        for line in f:
            columns = line.split()
            record_dict = dict(zip(header, columns))
            # check if values are validated as per schema (integer and positive)
            for key in ['ccd', 'mary_run', 'date', 'cand_num']:
                if type(record_dict.get(key)) is not int:
                    raise TableValueError(key + " is not an integer")
                if record_dict.get(key) < 0:
                    raise TableValueError(key + " needs to be positive")
                if record_dict.get(key) is None:
                    raise TableValueError(key + " is empty")

            # check if required values are numeric
            for key in ['ID','mag', 'emag', 'mjd', 'RA', 'DEC']:
                if type(record_dict.get(key)) is not float:
                    raise TableValueError(key + " is not a float")
                if record_dict.get(key) is None:
                    raise TableValueError(key + " is empty")

            # check if required values are strings and not NULL
            for key in ['maryID', 'sci_path', 'sub_path', 'temp_path']:
                if type(record_dict.get(key)) is not str:
                    raise TableValueError(key + " is not a string")
                if record_dict.get(key) is None:
                    raise TableValueError(key + " is empty")

            if not 10.0 <= record_dict['mag'] <= 30.0:
                raise TableValueError("mag is out of bounds")
            if not 0.0 <= record_dict['RA'] <= 360.0:
                raise TableValueError("RA is out of bounds")
            if not -90.0 <= record_dict['DEC'] <= 90.0:
                raise TableValueError("DEC is out of bounds")
        f.close()

    def add_post(self, author=None, maryid=None, body=None):
        """adds a dictionary of comments to the database"""
        if not author:
            print("author required")
        if not maryid:
            print("maryID required")
        if not body:
            print("comment required")

        self.post = post_dict

    def send_record(self):
        """send records to database"""

        package = "web"
        method = "create"
        json_payload = self.record
        print("Sending request", json_payload)
        try:
            r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
            if r.status_code == request.codes.OK:
                return r.get_json()
            else:
                print("failed request status code ", r.status_code)
        except:
            # logging.error("failed")
            print("failed request, check response")
            return(r.content)


    def send_post(self):
        """send records to database"""

        package = "web"
        method = "posts/create"
        post_payload = self.post

        try:
            r = requests.post(f"{self.api_url}/{package}/{method}", json=post_payload)
            if r.status_code == request.codes.OK:
                return r.get_json()
            else:
                print("failed request")
        except:
            # logging.error("failed")
            print("failed")

        # db = get_db()
        # db.execute(
        #     'INSERT INTO post (title, body, author_id)'
        #     ' VALUES (?, ?, ?)',
        #     (title, body, g.user['id'])
        # )
        # db.commit()

    # #
    # # Web methods
    # #
    #
    # # call_stage_1
    # def call_get_run(self):
    #     package = "web"
    #     method = "stage_1"
    #     json_payload = {}
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.OK:
    #         return r.get_json()
    #     else:
    #         print("failed request")
    #
    # # call_stage_2
    # def call_get_image_metadata(self):
    #     package = "web"
    #     method = "stage_2"
    #     json_payload = {}
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.OK:
    #         return r.get_json()
    #     else:
    #         print("failed request")

    def set_point(self, xy):
        '''creates a sky coord object from a list with two entries'''
        self.point = SkyCoord(xy[0]*u.deg, xy[1]*u.deg, frame='icrs')


    def get_distance(self, c1, c2):
        ''' returns the angular distance between two points on sky '''
        self.c1 = SkyCoord(c1[0]*u.deg, c1[1]*u.deg, frame='icrs')
        self.c2 = SkyCoord(c2[0]*u.deg, c2[1]*u.deg, frame='icrs')
        d = self.c1.separation(self.c2)
        return(d.radian)


    #     if request.method == 'POST':
    #         title = request.form['title']
    #         body = request.form['body']
    #         error = None
    #
    #     #     if not title:
    #     #         error = 'Title is required.'
    #     #
    #     #     if error is not None:
    #     #         flash(error)
    #     #     else:
    #     #         db = get_db()
    #     #         db.execute(
    #     #             'INSERT INTO post (title, body, author_id)'
    #     #             ' VALUES (?, ?, ?)',
    #     #             (title, body, g.user['id'])
    #     #         )
    #     #         db.commit()
    #     #         return redirect(url_for('blog.index'))
    #     #
    #     # return render_template('blog/create.html')
    #
    # def get_post(id, check_author=True):
    #     post = get_db().execute(
    #         'SELECT p.id, title, body, created, author_id, username'
    #         ' FROM post p JOIN user u ON p.author_id = u.id'
    #         ' WHERE p.id = ?',
    #         (id,)
    #     ).fetchone()
    #
    #     if post is None:
    #         abort(404, "Post id {0} doesn't exist.".format(id))
    #
    #     if check_author and post['author_id'] != g.user['id']:
    #         abort(403)
    #
    #     return post
    #
    # # call_stage_1
    # def call_stage_1(self, id, value):
    #     package = "workflow"
    #     method = "stage_1"
    #     json_payload = {
    #         "id": id,
    #         "value": value
    #     }
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.NO_CONTENT:
    #         print("Sucessfully made reqest")
    #     else:
    #         print("failed request")
    #
    # # call_stage_2
    # def call_stage_2(self, id, amount):
    #     package = "workflow"
    #     method = "stage_2"
    #     json_payload = {
    #         "id": id,
    #         "value": amount
    #     }
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.NO_CONTENT:
    #         print("Sucessfully made reqest")
    #     else:
    #         print("failed request")
    #
    #
    # #
    # # Web methods
    # #
    #
    # # call_stage_1
    # def call_get_run(self):
    #     package = "web"
    #     method = "stage_1"
    #     json_payload = {}
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.OK:
    #         return r.get_json()
    #     else:
    #         print("failed request")
    #
    # # call_stage_2
    # def call_get_image_metadata(self):
    #     package = "web"
    #     method = "stage_2"
    #     json_payload = {}
    #
    #     try:
    #         r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
    #     except as e:
    #         logging.error("failed")
    #
    #     if r.status_code == requests.codes.OK:
    #         return r.get_json()
    #     else:
    #         print("failed request")
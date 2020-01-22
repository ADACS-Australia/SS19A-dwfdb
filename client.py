import requests
from .errors import *
from astropy.io import ascii
import pandas as pd
import numpy as np
#
# from astropy import units as u
# from astropy.coordinates import SkyCoord

# Define a class
class Client(object):
    def __init__(self, api_url=None, sender=None):
        self.api_url = api_url
        self.sender = sender
        self.batch = None
        self.record = None
        self.point = None
        self.post = None

    def host(self,api_url):
        self.api_url = api_url

    def author(self, sender):
        """set the author/sender of the data packets"""
        self.sender = sender

    #
    # Workflow methods - adding the data and checking basic record requirements
    #
    def add_record(self, record_dict):
        """creates the dictionary of records and checks data is acceptable"""

        # check if values are validated as per schema (integer and positive)
        for key in ['id', 'ccd', 'mary_run', 'date', 'cand_num']:
            if type(record_dict.get(key)) is not int:
                raise TableValueError(key + " is not an integer")
            if record_dict.get(key) < 0:
                raise TableValueError(key + " needs to be positive")
            if record_dict.get(key) is None:
                raise TableValueError(key + " is empty")

        # check if required values are numeric
        for key in ['mag', 'emag', 'mjd', 'ra', 'dec']:
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
        if not 0.0 <= record_dict['ra'] <= 360.0:
            raise TableValueError("RA is out of bounds")
        if not -90.0 <= record_dict['dec'] <= 90.0:
            raise TableValueError("DEC is out of bounds")

        self.record = record_dict

    def add_batch(self, filename):
        """adds content of ascii file of records to the database"""
        batchfile = ascii.read(filename)

        # turn ascii table to dictionary, example for one line
        bkey = batchfile.colnames
        for b in bkey:
            batchfile.rename_column(b, b.lower())
        batchfile.rename_column("maryid", "maryID")
        bkey = batchfile.colnames
        l = len(batchfile)
        df = pd.DataFrame({'index': int(), 'reason': []})
        for i in range(l):
            record_dict = dict(zip(bkey, batchfile[bkey][i]))
            for key in ['id', 'ccd', 'mary_run', 'date', 'cand_num']:
                j = int(record_dict.get(key))
                if j == record_dict.get(key):
                    record_dict[key] = int(record_dict[key])
                else:
                    df = df.append({'index': int(i), 'reason': f"{key} not an int"}, ignore_index=True)
                    # next
                if record_dict.get(key) < 0:
                    df = df.append({'index': int(i), 'reason': f"{key} needs to be positive"}, ignore_index=True)
                    # next
                if record_dict.get(key) is None:
                    df = df.append({'index': int(i), 'reason': f"{key} is empty"}, ignore_index=True)
                    # next

            # check if required values are numeric
            for key in ['mag', 'emag', 'mjd', 'ra', 'dec']:
                if not np.issubdtype(type(record_dict.get(key)), np.number):

                    df = df.append({'index': int(i), 'reason': f"{key} not a float"}, ignore_index=True)
                    # raise TableValueError(key + " is not a float")
                if record_dict.get(key) is None:
                    df = df.append({'index': int(i), 'reason': f"{key} is empty"}, ignore_index=True)
                    # raise TableValueError(key + " is empty")

            # check if required values are strings and not NULL
            for key in ['maryID', 'sci_path', 'sub_path', 'temp_path']:
                # if type(record_dict.get(key)) is not np.string:
                if not np.issubdtype(type(record_dict.get(key)), np.str_):
                    # a.dtype.type is np.string_
                    df = df.append({'index': int(i), 'reason': f"{key} not a string"}, ignore_index=True)
                    # raise TableValueError(key + " is not a string")
                if record_dict.get(key) is None:
                    df = df.append({'index': int(i), 'reason': f"{key} is empty"}, ignore_index=True)
                    # raise TableValueError(key + " is empty")

            if not 10.0 <= record_dict['mag'] <= 30.0:
                df = df.append({'index': int(i), 'reason': f"mag is out of bounds: {record_dict['mag']}"}, ignore_index=True)
                # raise TableValueError("mag is out of bounds")
            if not 0.0 <= record_dict['ra'] <= 360.0:
                df = df.append({'index': int(i), 'reason': f"RA is out of bounds: {record_dict['ra']}"},
                               ignore_index=True)
                # raise TableValueError("RA is out of bounds")
            if not -90.0 <= record_dict['dec'] <= 90.0:
                df = df.append({'index': int(i), 'reason': f"Dec is out of bounds: {record_dict['dec']}"}, ignore_index=True)
                # raise TableValueError("DEC is out of bounds")

            if any(df['index'] == i):
                print(f"There are issues with row {i}, please check returned dataframe")
                # next
            else:
                package = "web/run"
                method = "create"
                json_payload = record_dict
                print(f"Sending request, row {i}")
                try:
                    r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
                    if not r.status_code == requests.codes.OK:
                        df = df.append({'index': int(i), 'reason': f"failed request status code {r.status_code}"}, ignore_index=True)
                except Exception as e:
                    df = df.append({'index': int(i), 'reason': f"failed request, check response {e}"}, ignore_index=True)
                    # print("failed request, check response ", e)
        self.batch = df


    def add_post(self, author=None, maryid=None, body=None):
        """adds a dictionary of comments to the database"""

        if not author:
            author = self.sender
            if not author:
                print("author required")
        if not maryid:
            print("maryID required")
        if not body:
            print("comment required")
        post_dict = {'author':author, 'maryid': maryid, 'body': body}
        self.post = post_dict

    #
    # Workflow methods - sending data to the database
    #

    def send_record(self):
        """send records to database"""

        package = "web/run"
        method = "create"
        json_payload = self.record
        print("Sending request")
        try:
            r = requests.post(f"{self.api_url}/{package}/{method}", json=json_payload)
            if r.status_code == requests.codes.OK:
                return r.json()
            else:
                print("failed request status code ", r.status_code)
        except Exception as e:
            # logging.error("failed")
            print("failed request, check response ", e)
            # return(r)

    def update_record(self):
        """send records to database"""

        package = "web/run"
        json_payload = self.record
        method = f"{json_payload['maryID']}/update"

        print("Sending update request")
        try:
            r = requests.put(f"{self.api_url}/{package}/{method}", json=json_payload)
            if r.status_code == requests.codes.OK:
                return r.json()
            else:
                print("failed request status code ", r.status_code)
        except Exception as e:
            # logging.error("failed")
            print("failed request, check response ", e)
            # return(r)

    def send_post(self):
        """send records to database"""

        package = "web/post"
        method = "create"
        post_payload = self.post

        try:
            r = requests.post(f"{self.api_url}/{package}/{method}", json=post_payload)
            if r.status_code == requests.codes.OK:
                return r.json()
            else:
                print("failed request status code ", r.status_code)
        except Exception as e:
            # logging.error("failed")
            print("failed request ", e)


    def get_record(self, ra, dec, dist):
        ''' queries the DB in a cone search with central RA, DEC and distance dist '''

        package = "web/run"
        json_payload = {'ra':ra, 'dec':dec, 'd':dist}

        print(f"Sending query {json_payload}")
        try:
            r = requests.get(f"{self.api_url}/{package}", json=json_payload)
            return r
        except Exception as e:
            # logging.error("failed")
            print("failed request, check response ", e)
            # return(r)

    def get_post(self,maryid=None):
        ''' queries the DB in a cone search with central RA, DEC and distance dist '''

        package = "web/post"
        json_payload = {'maryID':maryid}

        print(f"Sending post query {json_payload}")
        try:
            r = requests.get(f"{self.api_url}/{package}", json=json_payload)
            return r
        except Exception as e:
            # logging.error("failed")
            print("failed request, check response ", e)
            # return(r)
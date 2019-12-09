import requests
from .errors import *
from astropy import units as u
from astropy.coordinates import SkyCoord

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
        f = open(filename, 'r')
        header = f.readline().split()
        for line in f:
            columns = line.split()
            record_dict = dict(zip(header, columns))
            # check if values are validated as per schema (integer and positive)
            for key in ['ccd', 'mary_run', 'date', 'cand_num']:
                if not record_dict.get(key).is_integer():
                    raise TableValueError(key + " is not an integer")
                else:
                    record_dict[key] = int(record_dict[key])
                if record_dict.get(key) < 0:
                    raise TableValueError(key + " needs to be positive")
                if record_dict.get(key) is None:
                    raise TableValueError(key + " is empty")


            # check if required values are numeric
            for key in ['id','mag', 'emag', 'mjd', 'ra', 'dec']:
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
        f.close()

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
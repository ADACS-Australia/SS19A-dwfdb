# SS19A-dwfdb
Flask app and client module for setting up and connecting to DWF database

### Requirements for package
please make sure packages in the requirements.txt file are installed. Examples below are for macOS/Linux:

```bash
# create a virtual env
python3 -m venv env

# to activate the environment
source env/bin/activate

# install required packages
pip install -r requirements.txt

```

### To set up the DB for the first time
Make sure a postgres server is installed

```bash
# update APP_SETTINGS to Config once development is finished
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql://<user>@localhost/dwfadacs"

python manage.py db init
python manage.py db migrate
python manage.py db upgrade

#python manage.py runserver
```

Once the server is running the client app can be used to populate the DB.

### To use the client
```python
from dwf_server import client as dwf

url = <url of DB>
client = dwf.Client(url,"rebecca")
```

An example notebook will be provided (WIP) to show the usage of the client methods.

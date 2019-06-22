from app import db


class Dwf(db.Model):
    __tablename__ = 'dwf'

    id = db.Column(db.Integer, nullable=False)
    field = db.Column(db.String(), nullable=False)
    ccd = db.Column(db.Integer, nullable=False)
    mary_run = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    cand_num = db.Column(db.Integer, nullable=False)
    mag = db.Column(db.Float, nullable=False)
    emag = db.Column(db.Float, nullable=False)
    mjd = db.Column(db.Float, nullable=False)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    maryID = db.Column(db.String(), primary_key=True, unique=True, nullable=False)
    sci_path = db.Column(db.String(), unique=True, nullable=False)
    sub_path = db.Column(db.String(), unique=True, nullable=False)
    temp_path = db.Column(db.String(), unique=True, nullable=False)
    post = db.relationship('Post', backref='candidate', lazy=True)


    def __init__(self, id, field, ccd, mary_run, date, cand_num, mag, emag, mjd, ra, dec, maryID, sci_path, sub_path, temp_path):
        self.id = id
        self.field = field
        self.ccd = ccd
        self.mary_run = mary_run
        self.date = date
        self.cand_num = cand_num
        self.mag = mag
        self.emag = emag
        self.mjd = mjd
        self.ra = ra
        self.dec = dec
        self.maryID = maryID
        self.sci_path = sci_path
        self.sub_path = sub_path
        self.temp_path = temp_path

    def __repr__(self):
        return '<Mary ID {}>'.format(self.maryID)

    def serialize(self):
        return({
        'id': self.id,
        'field': self.field,
        'ccd': self.ccd,
        'mary_run': self.mary_run,
        'date': self.date,
        'cand_num': self.cand_num,
        'mag': self.mag,
        'emag': self.emag,
        'mjd': self.mjd,
        'ra': self.ra,
        'dec': self.dec,
        'maryID': self.maryID,
        'sci_path': self.sci_path,
        'sub_path': self.sub_path,
        'temp_path': self.temp_path
        })

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String())
    created = db.Column(db.DateTime)
    body = db.Column(db.String())
    maryID = db.Column(db.String(),  db.ForeignKey('dwf.maryID'), nullable=False)


    def __init__(self, author, created, body, maryID):
        self.author = author
        self.created = created
        self.body = body
        self.maryID = maryID

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'maryID': self.id,
            'author': self.author,
            'created': self.created,
            'body': self.body
        }


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.script import Manager
#from flask.ext.migrate import Migrate, MigrateCommand

# Database Configurations
DATABASE = 'expdb'
PASSWORD = 'passwd'
USER = 'user1'
HOSTNAME = 'mysqlserver'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s'%(USER, PASSWORD, HOSTNAME, DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):

    # Data Model Expense Table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(120), unique=True)
    category = db.Column(db.String(50), unique=False)
    description = db.Column(db.Text, unique=False)
    link = db.Column(db.String(250), unique=False)
    status = db.Column(db.String(50), unique=False)
    estimated_costs = db.Column(db.String(10), unique=False)
    submit_date = db.Column(db.String(20), unique=False)
    decision_date = db.Column(db.String(20), unique=False)

    def __init__(self, name, email, category, description, link, status, estimated_costs, submit_date, decision_date):
        # initialize columns
        self.name = name
        self.email = email
        self.category = category
        self.description = description
        self.link = link
        self.status = status
        self.estimated_costs = estimated_costs
        self.submit_date = submit_date
        self.decision_date = decision_date
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
    def __repr__(self):
        return '<User %r>' % self.name
#db.drop_all()
db.create_all()
db.session.commit()

def createDB(hostname=None):
    if hostname != None:
        HOSTNAME = hostname
    import sqlalchemy
    engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI']) #sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME)) # connect to server
    engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE)) #create db


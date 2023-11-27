from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    labels = db.Column(db.String(255))

class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), nullable=False, unique=True)
    commit_message = db.Column(db.Text)


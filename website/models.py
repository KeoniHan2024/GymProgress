from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    first_name = db.Column(db.String(40))
    weights = db.relationship('Weight')


class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(200), nullable=False)
    date_worked = db.Column(db.DateTime(timezone="True"), default=func.now())
    weight = db.Column(db.Float, nullable=False)
    units = db.Column(db.Integer, nullable=False)     ## 0 lbs -- 1 kgs --
    reps = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)    ## Workout ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exercise_name = db.Column(db.String(200), nullable=False)       
    muscle_group = db.Column(db.String(100), nullable=False)

# class Macro(db.Model):

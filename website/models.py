from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    first_name = db.Column(db.String(40))
    weights = db.relationship('Weight', backref='user', lazy=True)
    workouts = db.relationship('Workout', backref='user', lazy=True)
    

    # user = User.query.get(user_id)  # Get a specific user
    # user_workouts = user.workouts  # Access all workouts of this user
    # user_weights = user.weights  # Access all weights of this user

class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(200), nullable=False)
    date_worked = db.Column(db.DateTime(timezone="True"), default=func.now())
    weight = db.Column(db.Float, nullable=False)
    units = db.Column(db.Integer, nullable=False)     ## 0 lbs -- 1 kgs
    reps = db.Column(db.Integer, nullable=False)

    # For weight-based exercises (e.g., sets, reps, weight)
    # weight = db.Column(db.Float, nullable=True)
    # reps = db.Column(db.Integer, nullable=True)
    # sets = db.Column(db.Integer, nullable=True)
    # units = db.Column(db.Integer, nullable=True)  # 0 = lbs, 1 = kgs
    
    # For time-based exercises (e.g., duration in seconds)
    # duration_seconds = db.Column(db.Integer, nullable=True)  # Time-based workouts
    
    # # For distance-based exercises (e.g., distance in meters or kilometers)
    # distance = db.Column(db.Float, nullable=True)  # Distance in meters or kilometers

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Workout ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # User ID who logged the workout
    exercise_name = db.Column(db.String(200), nullable=False)  # Name of the exercise (e.g., "Bench Press")
    # exercise_type = db.Column(db.String(50), nullable=False)  # Type of exercise: "weight", "time", "distance"
    
    # Relationship to link workouts with muscle groups through the association table
    muscles = db.relationship('WorkoutMuscle', back_populates='workout', cascade="all, delete")  # Added cascade here

    def __repr__(self):
        return f"<Workout {self.exercise_name}>"


class WorkoutMuscle(db.Model):
    __tablename__ = 'workout_muscle'
    
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), primary_key=True)
    muscle_group_id = db.Column(db.Integer, db.ForeignKey('muscle_group.id'), primary_key=True)
    
    # Relationship to link workouts with muscle groups
    workout = db.relationship('Workout', back_populates='muscles')
    muscle_group = db.relationship('MuscleGroup', back_populates='workouts')

    def __repr__(self):
        return f"<WorkoutMuscle workout_id={self.workout_id}, muscle_group_id={self.muscle_group_id}>"


class MuscleGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationship to link muscle groups with workouts
    workouts = db.relationship('WorkoutMuscle', back_populates='muscle_group')

    def __repr__(self):
        return f"<MuscleGroup {self.name}>"


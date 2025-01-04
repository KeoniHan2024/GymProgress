from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from .models import User, Workout, Weight
from . import db
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from sqlalchemy import case

views = Blueprint('views', __name__)

## this will run everytime we go to /root
@views.route('/',  methods=['POST','GET'])
@login_required
def home():
    # Retrieve the user-specific data
    user_id = current_user.id
    
    # Check if the form was submitted with a POST request
    unit = 'lbs'  # Default unit is lbs
    if request.method == 'POST':
        unit = request.form.get('unit_select', 'lbs')  # Get the selected unit (default to 'lbs')
    
    # Convert weight to the selected unit (kg or lbs)
    conversion_factor = 2.20462 if unit == 'kg' else 1  # kg to lbs conversion factor
    
    # Query the database to get the highest weight ever lifted for each exercise along with the reps
    exercise_prs = db.session.query(
        Weight.exercise_name,
        db.func.max(
            case(
                (Weight.units == 1, Weight.weight * 2.20462),  # Convert kg to lbs
                else_=Weight.weight  # Keep lbs as is
            )
        ).label('max_weight_lbs'),
        db.func.max(Weight.units).label('unit'),
        db.func.max(
            case(
                (Weight.units == 1, Weight.reps),  # Keep reps as is if the unit is kg
                else_=Weight.reps  # Reps for lbs
            )
        ).label('reps')  # Fetch the reps for the maximum weight
    ).filter_by(user_id=user_id).group_by(Weight.exercise_name).all()

    # Create a dictionary with exercise names as keys and their PR weights, reps, and units as values
    pr_data = {}
    for exercise in exercise_prs:
        exercise_name = exercise.exercise_name
        max_weight = exercise.max_weight_lbs if unit == 'lbs' else exercise.max_weight_lbs / 2.20462  # Convert back to kg if needed
        reps = exercise.reps  # Get the number of reps for the maximum weight
        unit_label = unit  # Display either 'lbs' or 'kg' based on the selected unit
        
        pr_data[exercise_name] = {
            "weight": round(max_weight, 2),
            "reps": reps,
            "unit": unit_label
        }

    # Render the homepage template and pass the data
    return render_template('home.html', 
                           user=current_user, 
                           pr_data=pr_data, 
                           unit=unit)  # Pass the selected unit to the template



@views.route('/viewData', methods=['POST','GET'])   ## decorator
@login_required
def viewData():
    setData = Weight.query.filter_by(user_id=current_user.id).all()

    workoutList = []
    for exercise in setData:
    # Ensure exercise_name exists and is not empty or just spaces
        if exercise.exercise_name and exercise.exercise_name.strip():
            # Format the date to only show the date part (YYYY-MM-DD)
            formatted_date = exercise.date_worked.strftime('%Y-%m-%d') if exercise.date_worked else ''
            
            # Add the relevant data to workoutList
            workoutList.append((formatted_date, exercise.exercise_name, exercise.weight, exercise.reps, exercise.units))

    # Sort the setData by date and exercise name
    workoutList.sort(key=lambda x: (x[0], x[1]))  # Sort by date first, then exercise name

    # Group by date
    grouped_data = {}
    for dateWorked, exerciseName, weight, reps, units in workoutList:
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        ## creates variable for string that will be either "kg" or "lb"
        unitString = "lb" if units == 0 else "kg"

        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString))

    # Render the template and pass the grouped data and today's date
    return render_template('dataViewer.html', 
                           user=current_user,  # assuming `current_user` is from Flask-Login or a similar system
                           todaysDate=date.today(), 
                           grouped_data=grouped_data)


@views.route('/logData', methods=['POST','GET'])   ## decorator
@login_required
def dataEntry():
    ##ANCHOR - LOGGING A SET WORKOUT
    if request.method == 'POST':
        workoutName = request.form.get('workoutName')
        setDate = request.form.get('date')
        setWeight = request.form.get('weight')
        setReps = request.form.get('reps')
        weightUnit = request.form.get('weightUnit')  # Get the selected unit (lbs or kgs)

        if setDate:
            setDate = datetime.strptime(setDate, '%Y-%m-%d').date()

        # Process weight based on the unit selected
        if weightUnit == 'kgs':
            unitId = 1  # 1 represents kg
        else:
            unitId = 0  # 0 represents lbs (or no unit selected, default to 0)

        print(unitId)
        new_exercise = Weight(user_id=current_user.id, exercise_name=workoutName,date_worked=setDate, units=unitId, weight=setWeight, reps=setReps)
        db.session.add(new_exercise)
        db.session.commit()
        flash(f"{workoutName} set has been added.", category="success")


    # Fetch all workout names for the current user and filter out None or empty names
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    workout_names = [workout.exercise_name for workout in workouts if workout.exercise_name and workout.exercise_name.strip()]

    return render_template('dataEntry.html', user=current_user, todaysDate=date.today(), workout_names=workout_names)


@views.route('/createWorkout', methods=['POST','GET'])   ## decorator
@login_required
def workout():
    ##ANCHOR - ADDING A WORKOUT
    if request.method == 'POST':
        workoutName = request.form.get('workout_name')
        muscleGroup = request.form.get('muscle_group')

        
        workout = Workout.query.filter_by(user_id=current_user.id, exercise_name=workoutName).first()

        if workout:
            flash("This exercise already exists", category="error")
        elif not workoutName:
            flash("Please enter a workout name", category="error")
        elif not muscleGroup:
            flash("Please enter a muscle group", category="error")
        else:
            new_exercise = Workout(user_id=current_user.id, exercise_name=workoutName,muscle_group=muscleGroup)
            db.session.add(new_exercise)
            db.session.commit()
            flash(f"'{workoutName}' has been added.", category="success")

    workouts = Workout.query.filter_by(user_id=current_user.id).all()

    workoutList = []
    for workout in workouts:
        if workout.exercise_name and workout.muscle_group:
            workoutList.append((workout.exercise_name, workout.muscle_group))
        
    return render_template('workout.html', user=current_user, nameList=workoutList)



@views.route('/delete_exercise/<exercise_name>', methods=['GET'])
def delete_exercise(exercise_name):
    # Assuming you have a Workout model with an 'exercise_name' attribute
    workout = Workout.query.filter_by(exercise_name=exercise_name).first()  # Find the workout by its name

    if workout:
        db.session.delete(workout)  # Delete the workout from the database
        db.session.commit()  # Commit the change to the database
    
    return redirect(url_for('views.workout'))  # Redirect to the page that displays the exercises

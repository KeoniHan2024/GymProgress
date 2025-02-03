from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from .models import User, Workout, Weight, MuscleGroup, WorkoutMuscle
from . import db
from datetime import datetime
from sqlalchemy import case
from collections import defaultdict

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
            workoutList.append((formatted_date, exercise.exercise_name, exercise.weight, exercise.reps, exercise.units, exercise.id))

    # Sort the setData by date and exercise name
    workoutList.sort(key=lambda x: (x[0], x[1]), reverse=True)  # Sort by date first, then exercise name

    # Group by date
    grouped_data = {}
    for dateWorked, exerciseName, weight, reps, units, id in workoutList:
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        ## creates variable for string that will be either "kg" or "lb"
        unitString = "lb" if units == 0 else "kg"
        setId = id

        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString, setId))

    # Render the template and pass the grouped data and today's date
    return render_template('dataViewer.html', 
                           user=current_user,  # assuming `current_user` is from Flask-Login or a similar system
                           todaysDate=date.today(), 
                           grouped_data=grouped_data)


@views.route('/logData', methods=['POST','GET'])   ## decorator
@login_required
def logData():
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

    
    setData = Weight.query.filter_by(user_id=current_user.id).all()
    workoutList = []
    for exercise in setData:
    # Ensure exercise_name exists and is not empty or just spaces
        if exercise.exercise_name and exercise.exercise_name.strip():
            # Format the date to only show the date part (YYYY-MM-DD)
            formatted_date = exercise.date_worked.strftime('%Y-%m-%d') if exercise.date_worked else ''
            
            # Add the relevant data to workoutList
            workoutList.append((formatted_date, exercise.exercise_name, exercise.weight, exercise.reps, exercise.units, exercise.id))

    # Sort the setData by date and exercise name
    workoutList.sort(key=lambda x: (x[0], x[1]), reverse=True)  # Sort by date first, then exercise name

    # Group by date
    grouped_data = {}
    for dateWorked, exerciseName, weight, reps, units, id in workoutList:
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        ## creates variable for string that will be either "kg" or "lb"
        unitString = "lb" if units == 0 else "kg"
        setId = id

        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString, setId))

    return render_template('addSet.html', user=current_user, todaysDate=date.today(), workout_names=workout_names, grouped_data=grouped_data)


# @views.route('/createWorkout', methods=['POST','GET'])   ## decorator
# @login_required
# def workout():
#     # ##ANCHOR - ADDING A WORKOUT
#     # if request.method == 'POST':
#     #     workoutName = request.form.get('workout_name')
#     #     muscleGroup = request.form.get('muscle_group')

        
#     #     workout = Workout.query.filter_by(user_id=current_user.id, exercise_name=workoutName).first()

#     #     if workout:
#     #         flash("This exercise already exists", category="error")
#     #     elif not workoutName:
#     #         flash("Please enter a workout name", category="error")
#     #     elif not muscleGroup:
#     #         flash("Please enter a muscle group", category="error")
#     #     else:
#     #         new_exercise = Workout(user_id=current_user.id, exercise_name=workoutName,muscle_group=muscleGroup)
#     #         db.session.add(new_exercise)
#     #         db.session.commit()
#     #         flash(f"'{workoutName}' has been added.", category="success")

#     # workouts = Workout.query.filter_by(user_id=current_user.id).all()

#     # workoutList = []
#     # for workout in workouts:
#     #     if workout.exercise_name:
#     #         # Get the list of muscle names associated with the current workout
#     #         muscles = [wm.muscle.name for wm in workout.muscles]
            
#     #         # Append the exercise name along with its associated muscles to the workoutList
#     #         workoutList.append((workout.exercise_name, ", ".join(muscles)))
        
#     # return render_template('workout.html', user=current_user, nameList=workoutList)

#     # Fetch muscle group names from the database
#     muscle_groups = MuscleGroup.query.all()

#      # Create a list of dictionaries with 'id' and 'name' for each muscle
#     muscle_names = [{'id': muscle.id, 'name': muscle.name} for muscle in muscle_groups]

#     # If the form is submitted, process the data
#     if request.method == 'POST':
#         workout_name = request.form.get('workout_name')
#         muscles_input = request.form.get('muscles')  # This will contain the comma-separated tags
#         print(muscles_input)

#         # Process form submission (save to DB or perform other logic)
#         # For example, split and save the muscles
#         muscles_list = [muscle.strip() for muscle in muscles_input.split(',')]

#         return redirect(url_for('views.workout'))

#     return render_template('workout.html', user=current_user, muscle_names=muscle_names)
@views.route('/createWorkout', methods=['POST', 'GET'])
@login_required
def workout():
    if request.method == 'POST':
        workout_name = request.form.get('workout_name')
        muscles_ids_input = request.form.get('muscles_ids')  # Get the comma-separated muscle IDs
        # workout_type = request.form.get('workout-type')  # Get the comma-separated muscle IDs
        
        # Ensure muscles_ids_input is not None and is not empty
        if muscles_ids_input:
            muscle_ids = [int(id.strip()) for id in muscles_ids_input.split(',')]  # Convert IDs to integers
        else:
            muscle_ids = []

        # Create a new workout entry
        new_workout = Workout(user_id=current_user.id, exercise_name=workout_name)
        db.session.add(new_workout)
        db.session.commit()  # Commit to save the workout

        # Create the association in the WorkoutMuscle table
        for muscle_id in muscle_ids:
            workout_muscle = WorkoutMuscle(workout_id=new_workout.id, muscle_group_id=muscle_id)
            db.session.add(workout_muscle)

        db.session.commit()  # Final commit to save the associations

        flash(f"'{workout_name}' has been added.", category="success")
        return redirect(url_for('views.workout'))

    # Fetch muscle group names from the database for the form
    muscle_groups = MuscleGroup.query.all()
    muscle_names = [{'name': muscle.name, 'id': muscle.id} for muscle in muscle_groups]

    # Query all workouts for the current user
    workouts = Workout.query.filter_by(user_id=current_user.id).all()

    workout_list = []
    for workout in workouts:
        # Get the muscle groups associated with the current workout
        muscles = [wm.muscle_group.name for wm in workout.muscles]

        # Append the workout name and its associated muscle groups to the list
        workout_list.append({
            'exercise_id': workout.id,
            'exercise_name': workout.exercise_name,
            'muscle_groups': ", ".join(muscles)  # Join muscle groups with a comma
        })
    
    return render_template('workout.html', user=current_user, muscle_names=muscle_names, nameList=workout_list)


@views.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    # Find the workout by its ID and ensure it belongs to the logged-in user
    workout = Workout.query.filter_by(id=exercise_id, user_id=current_user.id).first()

    # Check if the workout exists
    if workout:
        db.session.delete(workout)  # Delete the workout
        db.session.commit()  # Commit the deletion
        flash(f"'{workout.exercise_name}' has been deleted.", category="success")
    else:
        flash("Workout not found or you don't have permission to delete this workout.", category="error")

    # Redirect back to the workouts list page
    return redirect(url_for('views.workout'))


@views.route('/edit_set/<int:set_id>', methods=['GET', 'POST'])
@login_required
def edit_set(set_id):
    set_to_edit = Weight.query.get_or_404(set_id)
    
    if request.method == 'POST':
        # Get the new values from the form (you will need to create a form for the edit)
        set_to_edit.reps = request.form['reps']
        set_to_edit.weight = request.form['weight']
        db.session.commit()
        
        flash("Set updated successfully", "success")
        return redirect(url_for('views.viewData'))  # Or wherever you want to redirect
    
    return render_template('edit_set.html', user=current_user, set=set_to_edit)

@views.route('/edit_set_logPage/<int:set_id>', methods=['GET', 'POST'])
@login_required
def edit_set_logPage(set_id):
    set_to_edit = Weight.query.get_or_404(set_id)
    
    if request.method == 'POST':
        # Get the new values from the form (you will need to create a form for the edit)
        set_to_edit.reps = request.form['reps']
        set_to_edit.weight = request.form['weight']
        db.session.commit()
        
        flash("Set updated successfully", "success")
        return redirect(url_for('views.logData'))  # Or wherever you want to redirect
    
    return render_template('edit_set.html', user=current_user, set=set_to_edit)


@views.route('/delete_set/<int:set_id>', methods=['POST'])
@login_required
def delete_set(set_id):
    set_to_delete = Weight.query.get_or_404(set_id)
    
    db.session.delete(set_to_delete)
    db.session.commit()
    
    flash("Set deleted successfully", "success")
    return redirect(url_for('views.viewData'))  # Or wherever you want to redirect

@views.route('/delete_set_logPage/<int:set_id>', methods=['POST'])
@login_required
def delete_set_logPage(set_id):
    set_to_delete = Weight.query.get_or_404(set_id)
    
    db.session.delete(set_to_delete)
    db.session.commit()
    
    flash("Set deleted successfully", "success")
    return redirect(url_for('views.logData'))  # Or wherever you want to redirect


@views.route('/filtered_exercises', methods=['GET'])
@login_required
def filtered_exercises():
    # Retrieve filter type from request arguments
    filter_type = request.args.get('filterType')

    # Initialize an empty list to store the filtered data
    grouped_data = []

    if filter_type == 'dateRange':
        # Retrieve start and end dates from the request
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # Validate that both start and end dates are provided
        if start_date and end_date:
            # Call a function to fetch data filtered by the date range
            grouped_data = get_exercises_by_date_range(start_date, end_date)
        else:
            # Handle the case where dates are missing
            grouped_data = get_all_exercises()  # Fetch all data or handle as needed
    
    elif filter_type == 'exerciseName':
        # Retrieve the exercise name from the request
        exercise_name = request.args.get('exerciseName')
        
        print(exercise_name)
        
        if exercise_name:
            # Call a function to fetch data filtered by exercise name
            grouped_data = get_exercises_by_name(exercise_name)
        else:
            # Handle the case where no exercise name is provided
            grouped_data = get_all_exercises()  # Fetch all data or handle as needed
    
    else:
        # If no filter is selected, fetch all exercises
        grouped_data = get_all_exercises()

    return render_template('addSet.html', user=current_user, todaysDate=date.today(), grouped_data=grouped_data)




def get_exercises_by_date_range(startDate, endDate):
    # Query items between the date range for the current user
    workoutList = Weight.query.filter(
        Weight.date_worked.between(startDate, endDate),
        Weight.user_id == current_user.id
    ).all()

    # Group by date
    grouped_data = {}
    
    for workout in workoutList:
        # Access the attributes of the Weight model using dot notation
        dateWorked = workout.date_worked  # 'date_worked' attribute
        exerciseName = workout.exercise_name  # 'exercise_name' attribute
        weight = workout.weight  # 'weight' attribute
        reps = workout.reps  # 'reps' attribute
        units = workout.units  # 'units' attribute
        id = workout.id  # 'id' attribute

        # Group by dateWorked
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}
        
        # Group by exerciseName within each dateWorked
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        # Create unit string based on units (0 for lb, 1 for kg)
        unitString = "lb" if units == 0 else "kg"
        
        # Append the data as a tuple (weight, reps, unitString, setId)
        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString, id))
    
    return grouped_data

def get_all_exercises():
    # Fetch all workout names for the current user and filter out None or empty names
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    workout_names = [workout.exercise_name for workout in workouts if workout.exercise_name and workout.exercise_name.strip()]

    
    setData = Weight.query.filter_by(user_id=current_user.id).all()
    workoutList = []
    for exercise in setData:
    # Ensure exercise_name exists and is not empty or just spaces
        if exercise.exercise_name and exercise.exercise_name.strip():
            # Format the date to only show the date part (YYYY-MM-DD)
            formatted_date = exercise.date_worked.strftime('%Y-%m-%d') if exercise.date_worked else ''
            
            # Add the relevant data to workoutList
            workoutList.append((formatted_date, exercise.exercise_name, exercise.weight, exercise.reps, exercise.units, exercise.id))

    # Sort the setData by date and exercise name
    workoutList.sort(key=lambda x: (x[0], x[1]), reverse=True)  # Sort by date first, then exercise name

    # Group by date
    grouped_data = {}
    for dateWorked, exerciseName, weight, reps, units, id in workoutList:
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        ## creates variable for string that will be either "kg" or "lb"
        unitString = "lb" if units == 0 else "kg"
        setId = id

        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString, setId))

    return grouped_data


def get_exercises_by_name(name):
    # Query all workouts for the current user where exercise_name contains the given name (case-insensitive)
    workoutList = Weight.query.filter(
        Weight.user_id == current_user.id, 
        Weight.exercise_name.ilike(f'%{name}%')  # This searches for partial matches
    ).all()

    # Group by exercise_name and date_worked (dictionary format)
    grouped_data = {}

    for workout in workoutList:
        # Access the attributes of the Weight model using dot notation
        dateWorked = workout.date_worked  # 'date_worked' attribute
        exerciseName = workout.exercise_name  # 'exercise_name' attribute
        weight = workout.weight  # 'weight' attribute
        reps = workout.reps  # 'reps' attribute
        units = workout.units  # 'units' attribute
        id = workout.id  # 'id' attribute

        # First, group by dateWorked
        if dateWorked not in grouped_data:
            grouped_data[dateWorked] = {}

        # Then, group by exerciseName within each date
        if exerciseName not in grouped_data[dateWorked]:
            grouped_data[dateWorked][exerciseName] = []

        # Create unit string based on units (0 for lb, 1 for kg)
        unitString = "lb" if units == 0 else "kg"

        # Append the data as a tuple (weight, reps, unitString, setId)
        grouped_data[dateWorked][exerciseName].append((weight, reps, unitString, id))

    return grouped_data




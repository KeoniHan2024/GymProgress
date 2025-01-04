from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        ## there is a user and the password is correct for this user
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in Successfully", category="success")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect Password", category="error")
        else:
            flash("User does not exist", category="error")

            

    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check if the user already exists by the provided email
        user = User.query.filter_by(email=email).first()

        # If the user with the email already exists
        if user:
            flash("An account with this email already exists", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters", category="error")
        elif len(firstName) < 2:
            flash("First name must be greater than 1 character", category="error")
        elif password1 != password2:
            flash("Passwords do not match", category="error")
        elif len(password1) < 7:
            flash("Passwords must be greater than 6 characters", category="error")
        else:
            # Add the new user to the database
            new_user = User(email=email, password=generate_password_hash(password1, method='scrypt'), first_name=firstName)
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the newly created user
            login_user(new_user, remember=True)
            
            # Flash a success message and redirect to the home page
            flash("User has been created", category="success")
            return redirect(url_for('views.home'))

    return render_template('signup.html', user=current_user)





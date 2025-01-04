from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

# from flask import Flask
# from flask import render_template
# from flask import request, redirect

# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gymProgress.db'

# ## initialize DB
# db = SQLAlchemy(app)

# ## create db model
# class gymProgress(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     exercise_name = db.Column(db.String(200), nullable=False)
#     date_worked = db.Column(db.DateTime, default=datetime.now)
#     weight = db.Column(db.Float, nullable=False)
#     reps = db.Column(db.Integer, nullable=False)
#     sets = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return '<Name %r>' % self.id

# @app.route('/')
# def homepage():
#     return render_template('index.html', message='Hello, World!')

# @app.route('/login')
# def loginPage():
#     return render_template('login.html')

# @app.route('/signup')
# def signupPage():
#     return render_template('signup.html')

# @app.route('/logger', methods=['POST','GET'])
# def loggerPage():
#     if request.method == 'POST':
#         name = request.form['name']
#         newExercise = gymProgress(exercise_name=name, weight=float(0.1), reps=2, sets=1)

#         ## push to database
#         try:
#             db.session.add(newExercise)
#             db.session.commit()
#             return redirect('/logger')
#         except:
#             return "There was an error adding the exercise"
#     else:
#         exercise_list = gymProgress.query.order_by(gymProgress.date_worked)
#         return render_template('logger.html', exercises=exercise_list)


# @app.route('/greet', methods=['POST'])
# def greet():
#     name = request.form['name']
#     return f'Hello, {name}!'
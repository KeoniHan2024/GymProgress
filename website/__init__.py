from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gymprogressKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Importing blueprint
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Weight, MuscleGroup

    create_database(app)  # Ensure the database is created

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # migrate = Migrate(app, db)
    return app


def create_database(app):
    # Ensure that the app context is active before creating the database
    with app.app_context():
        if not path.exists('website/' + DB_NAME):  # Check if the database exists
            db.create_all()  # Create the database tables
            print('Created Database!')

            from .models import MuscleGroup  # Ensure MuscleGroup is imported

            # Add default muscle groups if the table is empty
            if MuscleGroup.query.count() == 0:
                default_muscle_groups = [
                    # PUSH      CHEST DAY
                    'Chest',
                    'Upper Chest', 'Middle Chest', 'Lower Chest',

                    'Shoulders',
                    'Front Deltoid', 'Side Deltoid',

                    'Triceps',  
                    'Triceps - Long Head', 'Triceps - Medial Head', 'Triceps - Short Head',

                    # PULL      BACK DAY
                    'Back',
                    'Latissimus Dorsi',
                    'Upper Lats', 'Middle Lats', 'Lower Lats',

                    'Rear Deltoid', 

                    'Trapezius',    
                    'Upper Traps', 'Middle Traps', 'Lower Traps',

                    'Rhomboids',
                    'Rhomboids Major', 'Rhomboids Minor'

                    'Erector Spinae',

                    'Biceps',
                    'Biceps - Long Head', 'Biceps - Short Head', 'Brachialis',


                    # LEGS
                    'Quadriceps',
                    'Rectus femoris', 'Vastus lateralis', 'Vastus medialis', 'Vastus intermedius',

                    'Hamstrings',
                    'Biceps femoris', 'Semitendinosus', 'Semimembranosus',

                    'Glutes',
                    'Gluteus maximus', 'Gluteus medius', 'Gluteus minimus',

                    'Calves',
                    'Gastrocnemius', 'Soleus',

                    # CORE
                    'Core',
                    'Obliques',
                    'Hip Flexors'
                ]

                # Create MuscleGroup objects and add them to the session
                for muscle_name in default_muscle_groups:
                    muscle_group = MuscleGroup(name=muscle_name)
                    db.session.add(muscle_group)

                db.session.commit()  # Commit the transaction to save the default data
                print('Added default muscle groups to the database!')




            # # Query all muscle groups and print them for debugging
            # muscle_groups = MuscleGroup.query.all()  # Get all muscle groups

            # print("== Debug: Listing All Muscle Groups ==")
            # for muscle_group in muscle_groups:
            #     print(f'Muscle Group ID: {muscle_group.id}, Name: {muscle_group.name}')

##############################################################################
# SOURCES CITED:
#
# The structure for the code in this file and default parameters
# is based on Flask's tutorial and the tutorial in the blog cited below:
# Flask. (Nov. 14, 2022) "Application Setup."
# [Flask v.2.2.x documentation/tutorial].
# https://flask.palletsprojects.com/en/2.2.x/tutorial/factory/
#
# Birchard, T. (Oct. 24, 2022) "Demystifying the Flask Application Factory."
# Hackers and Slackers [Blog].
# https://hackersandslackers.com/flask-application-factory/
#
# Separating the routes into the logical structure shown here and in the
# app_routes folder is based on the example in
# Birchard, T. (Oct. 24, 2022) "Demystifying the Flask Application Factory."
# Hackers and Slackers [Blog].
# https://hackersandslackers.com/flask-application-factory/
##############################################################################
from flask import Flask
from flask_mysqldb import MySQL

# db available globally

db = MySQL()


def init_app():
    """
    Initializes routes and registers blueprints.
    Allows logic to be modularized.
    """
    app = Flask(__name__, instance_relative_config=False)
    # Configuration comes from the Config class in config.py
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)

    # Imports modularized logic into the app
    with app.app_context():
        from .app_routes import index
        from .app_routes import buses
        from .app_routes import bus_stops
        from .app_routes import drivers
        from .app_routes import driver_routes
        from .app_routes import routes
        from .app_routes import route_stops
        from .app_routes import ridership

        return app

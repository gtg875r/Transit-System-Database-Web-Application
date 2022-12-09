##############################################################################
# SOURCES CITED:
#
# The code in this file was adapted from the OSU CS340 Flask Starter Guide:
# gkochera. (Oct. 24, 2022) "Flask Starter App" [Guide and starter code].
# https://github.com/osu-cs340-ecampus/flask-starter-app
#
# It is also based on the code in
# https://hackersandslackers.com/flask-application-factory/
##############################################################################
import os

# from app import app
from application import init_app

app = init_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 35462))
    app.run(port=port, debug=True)
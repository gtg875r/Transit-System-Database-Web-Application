##############################################################################
# SOURCES CITED:
#
# The code in this file was adapted from the OSU CS340 Flask Starter Guide
# and the code example in the blog cited below:
# gkochera. (Oct. 24, 2022) "Flask Starter App" [Guide and starter code].
# https://github.com/osu-cs340-ecampus/flask-starter-app
#
# Birchard, T. (Oct. 24, 2022) "Demystifying the Flask Application Factory."
# Hackers and Slackers [Blog].
# https://hackersandslackers.com/flask-application-factory/
##############################################################################
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    MYSQL_HOST = "classmysql.engr.oregonstate.edu"
    MYSQL_USER = "cs340_fowleraa"
    MYSQL_PASSWORD = "0748"
    MYSQL_DB = "cs340_fowleraa"
    MYSQL_CURSORCLASS = "DictCursor"
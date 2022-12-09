##############################################################################
# SOURCES CITED:
#
# This code is based on and adapted from the OSU Flask starter code and the
# Flask documentation Quickstart guide:
# gkochera. (Oct. 24, 2022) "Flask Starter App" [OSU CS340 Guide and
# starter code]. https://github.com/osu-cs340-ecampus/flask-starter-app
#
# Flask. (Oct. 24, 2022) "Quickstart" [Flask v.2.2.x documentation]
# https://flask.palletsprojects.com/en/2.2.x/quickstart/#
#
# Code that executes the query and fetches the result is adapted from:
# gkochera. (Oct. 24, 2022) "Flask Starter App" [OSU CS340 Guide and
# starter code]. https://github.com/osu-cs340-ecampus/flask-starter-app
#
# Structure of queries, query parameters, and use of conditional statements in
# building queries and query parameters adapted from:
# gkochera. (Oct. 24, 2022) "Flask Starter App" [OSU CS340 Guide and
# starter code]. https://github.com/osu-cs340-ecampus/flask-starter-app
#
# Use of two route decorators for the stops() route based on the Flask documentation:
# Flask. (Dec. 4, 2022). "URL Route Registrations" in "API" in Flask documentation
# [Flask v. 2.2.x docs]. https://flask.palletsprojects.com/en/2.2.x/api/#url-route-registrations
#
# Use of request.args in form handling is adapted from:
# Flask. (Nov. 10, 2022) class flask.Request in "Incoming Request Data" in
# "API". [Flask v.2.2.x documentation].
# https://flask.palletsprojects.com/en/2.2.x/api/#flask.Request
#
# The database queries are based on the materials from the
# modules for this course and on the example given as part of the OSU CS340 assignment Project Step 3 Draft Version:
# Oregon State University. (Oct. 26, 2022) bsg_sample_data_manipulation_queries.sql [Example DML file].
# https://canvas.oregonstate.edu/courses/1890458/files/94269647?wrap=1
#
# Oregon State University. (Nov. 1, 2022) Course modules for CS340.
# https://canvas.oregonstate.edu/courses/1890458/modules
#
# We also consulted the MySQL documentation as we built our queries:
# MySQL. (Oct. 26, 2022-Dec. 5, 2022) MySQL 5.7 Reference Manual. [MySQL v. 5.7 docs].
# https://dev.mysql.com/doc/refman/5.7/en/
#
# USE of LIKE for handling case-insensitive search is based on:
# Stackoverflow. (Nov. 11, 2022) "SQL - Ignore case while searching for a string."
# https://stackoverflow.com/questions/16082575/sql-ignore-case-while-searching-for-a-string
##############################################################################
from flask import redirect, render_template, request, url_for
from flask import current_app as app
from application import db


# HELPER FUNCTIONS
def build_search_query(stop_name=None,
                       stop_latitude=None,
                       stop_longitude=None):
    """
    Builds the query and query parameters for the search function
    for Bus Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = "SELECT * FROM `Bus_Stops`;"    # Default query to select all bus stops
    query_params = None                     # Default query does not need params

    # Build query based on whether any search filters have been applied
    if stop_name and not stop_latitude and not stop_longitude:
        stop_name = "%" + stop_name + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_name` LIKE %s;"
        query_params = (stop_name,)
    elif stop_name and stop_latitude and not stop_longitude:
        stop_name = "%" + stop_name + "%"
        stop_latitude = "%" + stop_latitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_name` LIKE %s AND `stop_latitude` LIKE %s;"
        query_params = (stop_name, stop_latitude)
    elif stop_name and stop_longitude and not stop_latitude:
        stop_name = "%" + stop_name + "%"
        stop_longitude = "%" + stop_longitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_name` LIKE %s AND `stop_longitude` LIKE %s;"
        query_params = (stop_name, stop_longitude)
    elif stop_name and stop_latitude and stop_longitude:
        stop_name = "%" + stop_name + "%"
        stop_latitude = "%" + stop_latitude + "%"
        stop_longitude = "%" + stop_longitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_name` LIKE %s AND `stop_latitude` LIKE %s AND `stop_longitude` LIKE %s;"
        query_params = (stop_name, stop_latitude, stop_longitude)
    elif stop_latitude and not stop_name and not stop_longitude:
        stop_latitude = "%" + stop_latitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_latitude` LIKE %s"
        query_params = (stop_latitude,)
    elif stop_latitude and stop_longitude and not stop_name:
        stop_latitude = "%" + stop_latitude + "%"
        stop_longitude = "%" + stop_longitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_latitude` LIKE %s AND `stop_longitude` LIKE %s;"
        query_params = (stop_latitude, stop_longitude)
    elif stop_longitude and not stop_name and not stop_latitude:
        stop_longitude = "%" + stop_longitude + "%"
        query = "SELECT * FROM `Bus_Stops` WHERE `stop_longitude` LIKE %s;"
        query_params = (stop_longitude,)

    return query, query_params


def build_create_query(stop_name,
                       has_shelter,
                       has_bench,
                       has_trash,
                       stop_lat,
                       stop_long):
    """
    Builds the query and query parameters for the add stop function
    for Bus Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """

    # No need to check if params have value, that is checked prior to func call
    query = ("INSERT INTO `Bus_Stops` "
             "(`stop_name`, `bus_shelter`, `bench`, `trash`, `stop_latitude`, `stop_longitude`) "
             "VALUES (%s, %s, %s, %s, %s, %s);")
    query_params = (stop_name,
                    has_shelter,
                    has_bench,
                    has_trash,
                    stop_lat,
                    stop_long)

    return query, query_params


def build_update_query(updated_stop_name,
                       updated_shelter,
                       updated_bench,
                       updated_trash,
                       updated_stop_lat,
                       updated_stop_long,
                       stop_id):
    """
    Builds the query and query parameters for the update stop function
    for Bus Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = None
    params = None
    # Only stop_name is None
    if updated_stop_lat and updated_stop_long and not updated_stop_name:
        query = ("UPDATE `Bus_Stop` "
                 "SET `stop_latitude`=%s, `stop_longitude`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_lat,
                  updated_stop_long,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Only stop_latitude is None
    if updated_stop_name and updated_stop_long and not updated_stop_lat:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_name`=%s, `stop_longitude`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_name,
                  updated_stop_long,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Only stop_longitude is None
    if updated_stop_name and updated_stop_lat and not updated_stop_long:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_name`=%s, `stop_latitude`=%s, `stop_longitude`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_name,
                  updated_stop_long,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Shelter, bench, and trash can't be None due the way the form works
    if not updated_stop_name and not updated_stop_lat and not updated_stop_long:
        query = ("UPDATE `Bus_Stops` "
                 "SET `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Stop_name and stop_latitude are None
    if updated_stop_long and not updated_stop_name and not updated_stop_lat:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_longitutde`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_long,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Stop_name and stop_longitude are None
    if updated_stop_lat and not updated_stop_name and not updated_stop_long:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_latitude`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_lat,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Stop_latitude and stop_longitude are None
    if updated_stop_name and not updated_stop_lat and not updated_stop_long:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_name`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_name,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)
    # Nothing is None
    if updated_stop_name and updated_stop_lat and updated_stop_long:
        query = ("UPDATE `Bus_Stops` "
                 "SET `stop_name`=%s, `stop_latitude`=%s, `stop_longitude`=%s, `bus_shelter`=%s, `bench`=%s, `trash`=%s "
                 "WHERE `stop_id`=%s;")
        params = (updated_stop_name,
                  updated_stop_lat,
                  updated_stop_long,
                  updated_shelter,
                  updated_bench,
                  updated_trash,
                  stop_id)

    return query, params


# BUS STOP ROUTES
@app.route("/stops", methods=["GET", "POST"])
@app.route("/stops/<error>", methods=["GET", "POST"])
def stops(error=None):
    stop_to_update = request.args.get("stop_to_update")
    stop_name_filter = None
    stop_lat_filter = None
    stop_long_filter = None

    if request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("stops"))
    elif request.method == "POST" and "search-submit" in request.form.keys():
        try:
            stop_name_filter = (str(request.form.get("search_stop_name").strip())
                                if request.form.get("search_stop_name") else None)
            stop_lat_filter = (float(request.form.get("search_latitude").strip())
                               if request.form.get("search_latitude") else None)
            stop_long_filter = (float(request.form.get("search_longitude").strip())
                                if request.form.get("search_longitude") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("bus_stops", error=error))

    select_query = ("SELECT * FROM `Bus_Stops` WHERE `stop_id`=%s;"
                    if stop_to_update else None)
    select_query_params = (stop_to_update,) if stop_to_update else None

    # Build query and query params
    query, query_params = build_search_query(stop_name_filter,
                                             stop_lat_filter,
                                             stop_long_filter)

    # Execute the query and fetch results
    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested bus stop records. Try again!"
                cur.execute("SELECT * FROM `Bus_Stops`;")
                results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                stop_to_update = cur.fetchall()

                if len(stop_to_update) < 1:
                    stop_to_update = None
                    error = "Something went wrong! The selected bus stop was not found."
    except:
        error = "Unable to retrieve bus stop data!"

    # Pass query results to jinja template for use on stops page
    return render_template("stops.j2",
                           stops=results,
                           stop_to_update=stop_to_update,
                           error=error)


@app.route("/add-stop", methods=["GET", "POST"])
def add_stop():
    error = None
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            stop_name = (str(request.form.get("new_stop_name").strip())
                         if request.form.get("new_stop_name") else None)
            has_shelter = (int(request.form.get("new_shelter").strip())
                           if request.form.get("new_shelter") else None)
            has_trash = (int(request.form.get("new_trash").strip())
                         if request.form.get("new_trash") else None)
            has_bench = (int(request.form.get("new_bench").strip())
                         if request.form.get("new_bench") else None)
            stop_lat = (float(request.form.get("new_stop_latitude").strip())
                        if request.form.get("new_stop_latitude") else None)
            stop_long = (float(request.form.get("new_stop_longitude").strip())
                         if request.form.get("new_stop_longitude") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("stops", error=error))

        # Check for required fields before sending to DB
        if (stop_name is None or stop_lat is None or stop_long is None or
                has_shelter is None or has_bench is None or has_trash is None):
            error = "Missing required data."
            return redirect(url_for("stops", error=error))

        # Build query and query parameters
        query, query_params = build_create_query(stop_name,
                                                 has_shelter,
                                                 has_bench,
                                                 has_trash,
                                                 stop_lat,
                                                 stop_long)
        try:
            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to update record."

    return redirect(url_for("stops", error=error))


@app.route("/update-stop/<int:stop_id>", methods=["GET", "POST"])
def update_stop(stop_id):
    error = None
    print(request.form.keys())
    if request.method == "POST" and "cancel-update" in request.form.keys():
        return redirect(url_for("stops"))
    elif request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            updated_stop_name = (str(request.form.get("up_stop_name").strip())
                                 if request.form.get("up_stop_name") else None)
            updated_shelter = (int(request.form.get("up_shelter").strip())
                               if request.form.get("up_shelter") else None)
            updated_bench = (str(request.form.get("up_bench").strip())
                             if request.form.get("up_bench") else None)
            updated_trash = (int(request.form.get("up_trash").strip())
                             if request.form.get("up_trash") else None)
            updated_stop_lat = (float(request.form.get("up_stop_latitude").strip())
                                if request.form.get("up_stop_latitude") else None)
            updated_stop_long = (float(request.form.get("up_stop_longitude").strip())
                                 if request.form.get("up_stop_longitude") else None)
        except ValueError:
            error = "Incorrect data entered -- wrong type."
            return redirect(url_for("stops", error=error))

        # Build update query
        query, params = build_update_query(updated_stop_name,
                                           updated_shelter,
                                           updated_bench,
                                           updated_trash,
                                           updated_stop_lat,
                                           updated_stop_long,
                                           stop_id)
        try:
            # Execute query
            with db.connection.cursor() as cur:
                cur.execute(query, params)
                cur.connection.commit()
        except:
            error = "Unable to update record."

    # Updated bus information will be displayed in top table on bus stops page
    return redirect(url_for("stops", error=error))


@app.route("/delete-stop/<int:selected_stop_id>", methods=["GET", "POST"])
def delete_stop(selected_stop_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Bus_Stops` WHERE `stop_id`=%s;"
    query_params = (selected_stop_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected bus stop record."

    return redirect(url_for("stops", error=error))

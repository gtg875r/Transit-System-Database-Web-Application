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
# Use of two route decorators for the route_stops() route based on the Flask documentation:
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
def build_search_query(route_name=None, stop_name=None):
    """
    Builds the query and query parameters for the search function
    for Route_Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # Default query to select all route_stop records
    query = (
        "SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
        "AS route_name, Bus_Stops.stop_name AS stop_name "
        "FROM `Route_Stops` "
        "JOIN `Transit_Routes` "
        "ON Route_Stops.route_id = Transit_Routes.route_id "
        "JOIN `Bus_Stops` "
        "ON Route_Stops.stop_id = Bus_Stops.stop_id;"
    )

    # Default query does not need params
    query_params = None

    # Build query based on whether any search filters have been applied
    if route_name and stop_name:
        route_name = "%" + route_name + "%"
        stop_name = "%" + stop_name + "%"
        query = ("SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
                 "AS route_name, Bus_Stops.stop_name AS stop_name "
                 "FROM `Route_Stops` "
                 "JOIN `Transit_Routes` "
                 "ON Route_Stops.route_id = Transit_Routes.route_id "
                 "JOIN `Bus_Stops` "
                 "ON Route_Stops.stop_id = Bus_Stops.stop_id "
                 "WHERE Transit_Routes.route_name LIKE %s AND Bus_Stops.stop_name LIKE %s;")
        query_params = (route_name, stop_name)
    elif route_name and not stop_name:
        route_name = "%" + route_name + "%"
        query = ("SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
                 "AS route_name, Bus_Stops.stop_name AS stop_name "
                 "FROM `Route_Stops` "
                 "JOIN `Transit_Routes` "
                 "ON Route_Stops.route_id = Transit_Routes.route_id "
                 "JOIN `Bus_Stops` "
                 "ON Route_Stops.stop_id = Bus_Stops.stop_id "
                 "WHERE Transit_Routes.route_name LIKE %s;")
        query_params = (route_name,)
    elif stop_name and not route_name:
        stop_name = "%" + stop_name + "%"
        query = ("SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
                 "AS route_name, Bus_Stops.stop_name AS stop_name "
                 "FROM `Route_Stops` "
                 "JOIN `Transit_Routes` "
                 "ON Route_Stops.route_id = Transit_Routes.route_id "
                 "JOIN `Bus_Stops` "
                 "ON Route_Stops.stop_id = Bus_Stops.stop_id "
                 "WHERE Bus_Stops.stop_name LIKE %s;")
        query_params = (stop_name,)

    return query, query_params


def build_create_query(selected_route_id, selected_stop_id):
    """
    Builds the query and query parameters for the add stop function
    for Route_Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # No need to check if params have value, that is checked prior to func call
    query = ("INSERT INTO `Route_Stops` (Route_Stops.route_id, Route_Stops.stop_id) "
             "VALUES ("
             "(SELECT Transit_Routes.route_id FROM `Transit_Routes` WHERE Transit_Routes.route_id = %s), "
             "(SELECT Bus_Stops.stop_id FROM `Bus_Stops` WHERE Bus_Stops.stop_id = %s) "
             ");")
    query_params = (selected_route_id, selected_stop_id)

    return query, query_params


def build_update_query(up_route_id,
                       up_stop_id,
                       route_stops_id):
    """
    Builds the query and query parameters for the update route stop function
    for Route Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # Only passenger_entry is None
    # Some of this structure is based off the example in the
    # OSU Flask starter code (cited at top of file)

    # Due to extensive use of dropdown menus, the only None value that could
    # mean the user does not have an update to the field is the datetime field.
    # All other None values would specifically insert a NULL value into the
    # db.
    query = ("UPDATE `Route_Stops` "
             "SET `route_id`=%s, `stop_id`=%s "
             "WHERE `route_stops_id`=%s;")
    params = (up_route_id, up_stop_id, route_stops_id)

    return query, params


# ROUTE_STOP ROUTES
@app.route("/route-stops", methods=["GET", "POST"])
@app.route("/route-stops/<error>", methods=["GET", "POST"])
def route_stops(error=None):
    route_name_filter = None
    stop_name_filter = None
    route_stop_to_update = int(request.args.get("route_stop_to_update")) if request.args.get("route_stop_to_update") else None

    if request.method == "POST" and "search-submit" in request.form.keys():
        try:
            route_name_filter = (str(request.form.get("search_route_name").strip())
                                 if request.method == "POST" else None)
            stop_name_filter = (str(request.form.get("search_stop_name").strip())
                                if request.method == "POST" else None)
        except ValueError:
            error = "Incorrect data -- wrong type."
            return redirect(url_for("route_stops", error=error))
    elif request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("route_stops"))

    select_query = ("SELECT * FROM `Route_Stops` WHERE `route_stops_id`=%s;"
                    if route_stop_to_update else None)
    select_query_params = (route_stop_to_update,) if route_stop_to_update else None

    print(f"route id to update: {route_stop_to_update}")

    # Build query and query params
    query, query_params = build_search_query(route_name_filter,
                                             stop_name_filter)

    # To display available app_routes and stops in add form
    stops_query = "SELECT * FROM `Bus_Stops`;"
    routes_query = "SELECT * FROM `Transit_Routes`;"

    # Execute the query and fetch results
    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested route stop records. Try again!"
                query = (
                    "SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
                    "AS route_name, Bus_Stops.stop_name AS stop_name "
                    "FROM `Route_Stops` "
                    "JOIN `Transit_Routes` "
                    "ON Route_Stops.route_id = Transit_Routes.route_id "
                    "JOIN `Bus_Stops` "
                    "ON Route_Stops.stop_id = Bus_Stops.stop_id;"
                )
                cur.execute(query)
                results = cur.fetchall()

            cur.execute(stops_query)
            stop_results = cur.fetchall()

            cur.execute(routes_query)
            route_results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                route_stop_to_update = cur.fetchall()
                print(f"route to update record: {route_stop_to_update}")
                if len(route_stop_to_update) < 1:
                    route_stop_to_update = None
                    error = "Something went wrong! The selected log was not found."
    except:
        error = "Unable to retrieve route stops data!"

    # Pass query results to jinja template for use on route_stops page
    return render_template("route_stops.j2",
                           route_stops=results,
                           all_stops=stop_results,
                           all_routes=route_results,
                           route_stop_to_update=route_stop_to_update,
                           error=error)

@app.route("/update-route-stops/<int:route_stops_id>", methods=["GET", "POST"])
def update_route_stop(route_stops_id):
    error = None
    if request.method == "POST" and "cancel-update" in request.form.keys():
        return redirect(url_for("route_stops"))
    elif request.method == "POST":
        print(f"ROUTE STOP UPDATE: {request.form}")
        # Cast to correct data types to ensure data is as expected
        try:
            updated_route_name = (int(request.form.get("up_route_name").strip()) if request.form.get("up_route_name") else None)
            updated_stop_name = (int(request.form.get("up_stop_name").strip()) if request.form.get("up_stop_name") else None)
        except ValueError:
            error = "Incorrect data entered -- wrong type."
            return redirect(url_for("route_stops", error=error))

        if updated_route_name and updated_stop_name:
            query = "UPDATE `Route_Stops` SET `route_id`=%s, `stop_id`=%s WHERE `route_stops_id`=%s;"
            params = (updated_route_name, updated_stop_name, route_stops_id)
        else:
            # Updated route information will be displayed in top table on routes page
            query, params = build_update_query(updated_route_name,
                                               updated_stop_name,
                                               route_stops_id)

        try:
            # Execute query
            with db.connection.cursor() as cur:
                cur.execute(query, params)
                cur.connection.commit()
        except:
            error = "Unable to update record."

    # Updated ridership log information will be displayed in top table on ridership page
    return redirect(url_for("route_stops", error=error))


@app.route("/add-route-stop", methods=["GET", "POST"])
def add_route_stop():
    error = None
    # Cast to correct type
    if request.method == "POST":
        try:
            new_route_id = (int(request.form.get("new_route_id").strip())
                            if request.form.get("new_route_id") else None)
            new_stop_id = (int(request.form.get("new_stop_id").strip())
                           if request.form.get("new_stop_id") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("route_stops", error=error))

        # Check for required fields before sending to DB
        if new_route_id is None or new_stop_id is None:
            error = "Missing data"
            return redirect(url_for("route_stops", error=error))

        # Build query and query parameters
        query, query_params = build_create_query(new_route_id, new_stop_id)

        try:
            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to add route."

    return redirect(url_for("route_stops", error=error))


@app.route("/delete-route-stop/<int:selected_route_stop_id>", methods=["GET", "POST"])
def delete_route_stop(selected_route_stop_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Route_Stops` WHERE `route_stops_id`=%s;"
    query_params = (selected_route_stop_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected route stop."

    return redirect(url_for("route_stops", error=error))

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
# Use of two route decorators for the driver_routes() route based on the Flask documentation:
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
def build_search_query(driver_last_name=None, driver_first_name=None, route_name=None):
    """
    Builds the query and query parameters for the search function
    for Route_Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # Default query to select all route_stop records
    query = (
        "SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
        "AS driver_name, Transit_Routes.route_name AS route_name "
        "FROM `Driver_Routes` "
        "JOIN `Transit_Routes` "
        "ON Driver_Routes.route_id = Transit_Routes.route_id "
        "JOIN `Drivers` "
        "ON Driver_Routes.driver_id = Drivers.driver_id;"
    )

    # Default query does not need params
    query_params = None

    # Build query based on whether any search filters have been applied
    if driver_last_name and route_name and not driver_first_name:
        driver_name = "%" + driver_last_name + "%"
        route_name = "%" + route_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.last_name LIKE %s AND Transit_Routes.route_name LIKE %s;")
        query_params = (driver_name, route_name)
    elif driver_first_name and route_name and not driver_last_name:
        driver_name = "%" + driver_first_name + "%"
        route_name = "%" + route_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.first_name LIKE %s AND Transit_Routes.route_name LIKE %s;")
        query_params = (driver_name, route_name)
    elif driver_first_name and driver_last_name and route_name:
        driver_last_name = "%" + driver_last_name + "%"
        driver_first_name = "%" + driver_first_name + "%"
        route_name = "%" + route_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.last_name LIKE %s AND Drivers.first_name LIKE %s AND Transit_Routes.route_name LIKE %s;")
        query_params = (driver_last_name, driver_first_name, route_name)
    elif route_name and not driver_last_name and not driver_first_name:
        route_name = "%" + route_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Transit_Routes.route_name LIKE %s;")
        query_params = (route_name,)
    elif driver_last_name and not route_name and not driver_first_name:
        driver_name = "%" + driver_last_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.last_name LIKE %s;")
        query_params = (driver_name,)
    elif driver_first_name and driver_last_name and not route_name:
        driver_last_name = "%" + driver_last_name + "%"
        driver_first_name = "%" + driver_first_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.last_name LIKE %s AND Drivers.first_name LIKE %s;")
        query_params = (driver_last_name, driver_first_name)
    elif driver_first_name and not driver_last_name and not route_name:
        driver_name = "%" + driver_first_name + "%"
        query = ("SELECT DISTINCT `driver_routes_id`, CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                 "AS driver_name, Transit_Routes.route_name AS route_name "
                 "FROM `Driver_Routes` "
                 "JOIN `Transit_Routes` "
                 "ON Driver_Routes.route_id = Transit_Routes.route_id "
                 "JOIN `Drivers` "
                 "ON Driver_Routes.driver_id = Drivers.driver_id "
                 "WHERE Drivers.first_name LIKE %s;")
        query_params = (driver_name,)

    return query, query_params


def build_create_query(selected_driver_id, selected_route_id):
    """
    Builds the query and query parameters for the add stop function
    for Route_Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # No need to check if params have value, that is checked prior to func call
    query = ("INSERT INTO `Driver_Routes` (Driver_Routes.driver_id, Driver_Routes.route_id) "
             "VALUES ("
             "(SELECT Drivers.driver_id FROM `Drivers` WHERE Drivers.driver_id = %s), "
             "(SELECT Transit_Routes.route_id FROM `Transit_Routes` WHERE Transit_Routes.route_id = %s) "
             ");")
    query_params = (selected_driver_id, selected_route_id)

    return query, query_params


# DRIVER_ROUTES ROUTES
@app.route("/driver-routes", methods=["GET", "POST"])
@app.route("/driver-routes/<error>", methods=["GET", "POST"])
def driver_routes(error=None):
    driver_last_filter = None
    driver_first_filter = None
    route_name_filter = None

    if request.method == "POST" and "search-submit" in request.form.keys():
        try:
            driver_last_filter = (str(request.form.get("search_driver_last").strip())
                                  if request.method == "POST" else None)
            driver_first_filter = (str(request.form.get("search_driver_first").strip())
                                   if request.method == "POST" else None)
            route_name_filter = (str(request.form.get("search_route_name").strip())
                                 if request.method == "POST" else None)
        except ValueError:
            error = "Incorrect data -- wrong type."
            return redirect(url_for("driver_routes", error=error))
    elif request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("driver_routes"))

    # Build query and query params
    query, query_params = build_search_query(driver_last_filter,
                                             driver_first_filter,
                                             route_name_filter)

    # To display available app_routes and stops in add form
    driver_query = "SELECT * FROM `Drivers`;"
    routes_query = "SELECT * FROM `Transit_Routes`;"

    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested driver route records. Try again!"
                query = (
                    "SELECT DISTINCT `driver_routes_id`, "
                    "CONCAT(Drivers.first_name, ' ', Drivers.last_name)"
                    "AS driver_name, Transit_Routes.route_name AS route_name "
                    "FROM `Driver_Routes` "
                    "JOIN `Transit_Routes` "
                    "ON Driver_Routes.route_id = Transit_Routes.route_id "
                    "JOIN `Drivers` "
                    "ON Driver_Routes.driver_id = Drivers.driver_id;"
                )
                cur.execute(query)
                results = cur.fetchall()

            cur.execute(driver_query)
            driver_results = cur.fetchall()

            cur.execute(routes_query)
            route_results = cur.fetchall()
    except:
        error = "Unable to retrieve driver routes data!"

    # Pass query results to jinja template for use on route_stops page
    return render_template("driver_routes.j2",
                           driver_routes=results,
                           all_drivers=driver_results,
                           all_routes=route_results,
                           error=error)


@app.route("/add-driver-route", methods=["GET", "POST"])
def add_driver_route():
    error = None
    # Cast to correct type
    if request.method == "POST":
        try:
            print("TRY BLOCK")
            new_driver_id = (int(request.form.get("new_driver_id").strip())
                             if request.form.get("new_driver_id") else None)
            new_route_id = (int(request.form.get("new_route_id").strip())
                            if request.form.get("new_route_id") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("driver_routes", error=error))

        # Check for required fields before sending to DB
        if new_route_id is None or new_driver_id is None:
            error = "Missing data"
            return redirect(url_for("driver_routes", error=error))

        # Build query and query parameters
        query, query_params = build_create_query(new_driver_id, new_route_id)

        try:
            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to add your driver route. Try again."

    return redirect(url_for("driver_routes", error=error))


@app.route("/delete-driver-route/<int:selected_driver_route_id>", methods=["GET", "POST"])
def delete_driver_route(selected_driver_route_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Driver_Routes` WHERE `driver_routes_id`=%s;"
    query_params = (selected_driver_route_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected driver route record."
    return redirect(url_for("driver_routes", error=error))

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
# Use of two route decorators for the routes() route based on the Flask documentation:
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
def build_search_query(route_name_filter,
                       route_color_filter):
    """
    Builds the query and query parameters for the search function
    for Bus Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = "SELECT * FROM `Transit_Routes`;"   # Default query to select all routes
    query_params = None                         # Default query does not need params

    if route_name_filter and not route_color_filter:
        route_name_filter = "%" + route_name_filter + "%"
        query = "SELECT * FROM `Transit_Routes` WHERE `route_name` LIKE %s;"
        query_params = (route_name_filter,)
    elif route_name_filter and route_color_filter:
        route_name_filter = "%" + route_name_filter + "%"
        route_color_filter = "%" + route_color_filter + "%"
        query = "SELECT * FROM `Transit_Routes` WHERE `route_name` LIKE %s AND `route_color` LIKE %s;"
        query_params = (route_name_filter, route_color_filter)
    elif route_color_filter and not route_name_filter:
        route_color_filter = "%" + route_color_filter + "%"
        query = "SELECT * FROM `Transit_Routes` WHERE `route_color` LIKE %s;"
        query_params = (route_color_filter,)

    return query, query_params


# TRANSIT_ROUTES ROUTES
@app.route("/routes", methods=["GET", "POST"])
@app.route("/routes/<error>", methods=["GET", "POST"])
def routes(error=None):
    select_query = None
    select_query_params = None
    route_to_update = request.args.get("route_to_update")
    route_name_filter = None
    route_color_filter = None

    if request.method == "POST" and "search-submit" in request.form.keys():
        try:
            route_name_filter = str(request.form.get("search_route_name")) if request.form.get("search_route_name") else None
            route_color_filter = str(request.form.get("search_route_color")) if request.form.get("search_route_color") else None
        except ValueError:
            error = "Incorrect data -- wrong type."
            return redirect(url_for("routes", error=error))
    elif request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("routes"))

    if route_to_update:
        # Build query if a route has been selected for updating
        # This will be used populate the update form with the correct info
        select_query = "SELECT * FROM `Transit_Routes` WHERE `route_id`=%s;"
        select_query_params = (route_to_update,)

    query, query_params = build_search_query(route_name_filter, route_color_filter)

    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested route records. Try again!"
                cur.execute("SELECT * FROM `Transit_Routes`;")
                results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                route_to_update = cur.fetchall()

                if len(route_to_update) < 1:
                    route_to_update = None
                    error = "Something went wrong! The selected route was not found."
    except:
        error = "Unable to retrieve route data!"

    return render_template("routes.j2",
                           routes=results,
                           route_to_update=route_to_update,
                           error=error)


@app.route("/delete-route/<int:selected_route_id>", methods=["GET", "POST"])
def delete_route(selected_route_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Transit_Routes` WHERE `route_id`=%s;"
    query_params = (selected_route_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected route."

    return redirect(url_for("routes", error=error))


@app.route("/update-route/<int:route_id>", methods=["GET", "POST"])
def update_route(route_id):
    error = None
    query = None
    params = None
    # Cast to correct data types to ensure data is as expected
    try:
        updated_route_name = (str(request.form.get("up_route_name").strip())
                              if request.form.get("up_route_name") else None)
        updated_color = (str(request.form.get("up_color").strip())
                         if request.form.get("up_color") else None)
    except ValueError:
        error = "Incorrect data entered -- wrong type."
        return redirect(url_for("routes", error=error))

    if updated_route_name and updated_color:
        query = ("UPDATE `Transit_Routes` "
                 "SET `route_name`=%s, `route_color`=%s "
                 "WHERE `route_id`=%s;")
        params = (updated_route_name, updated_color, route_id)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, params)
            cur.connection.commit()
    except:
        error = "Unable to update record."

    # Updated route information will be displayed in top table on routes page
    return redirect(url_for("routes", error=error))


@app.route("/add-route", methods=["GET", "POST"])
def add_route():
    error = None
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            route_name = (str(request.form.get("new_route_name").strip())
                          if request.form.get("new_route_name") else None)
            route_color = (str(request.form.get("new_route_color").strip())
                           if request.form.get("new_route_color") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("routes", error=error))

        try:
            query = "INSERT INTO `Transit_Routes` (`route_name`, `route_color`) VALUES (%s, %s);"
            query_params = (route_name, route_color)

            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to add route to database."

    return redirect(url_for("routes", error=error))

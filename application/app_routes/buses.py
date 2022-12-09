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
# Use of two route decorators for the buses() route based on the Flask documentation:
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
def build_search_query(bus_num=None,
                       purchase_year=None,
                       bus_license=None):
    """
    Builds the query and query parameters for the search function
    for Buses.

    Returns the query and query parameters.

    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = "SELECT * FROM `Buses`;"    # Default query to select all buses
    query_params = None                 # Default query does not need params

    # Build query based on whether any search filters have been applied
    if bus_num and not bus_license and not purchase_year:
        query = "SELECT * FROM `Buses` WHERE `bus_number` LIKE %s;"
        query_params = (bus_num,)
    elif bus_num and bus_license and not purchase_year:
        bus_license = "%" + bus_license + "%"
        query = "SELECT * FROM `Buses` WHERE `bus_number` LIKE %s AND `license` LIKE %s;"
        query_params = (bus_num, bus_license)
    elif bus_num and purchase_year and not bus_license:
        query = "SELECT * FROM `Buses` WHERE `bus_number` LIKE %s AND `purchase_year` LIKE %s;"
        query_params = (bus_num, purchase_year)
    elif bus_num and bus_license and purchase_year:
        bus_license = "%" + bus_license + "%"
        query = "SELECT * FROM `Buses` WHERE `bus_number` LIKE %s AND `license` LIKE %s AND `purchase_year` LIKE %s;"
        query_params = (bus_num, bus_license, purchase_year)
    elif bus_license and not bus_num and not purchase_year:
        bus_license = "%" + bus_license + "%"
        query = "SELECT * FROM `Buses` WHERE `license` LIKE %s"
        query_params = (bus_license,)
    elif bus_license and purchase_year and not bus_num:
        bus_license = "%" + bus_license + "%"
        query = "SELECT * FROM `Buses` WHERE `license` LIKE %s AND `purchase_year` LIKE %s;"
        query_params = (bus_license, purchase_year)
    elif purchase_year and not bus_num and not bus_license:
        query = "SELECT * FROM `Buses` WHERE `purchase_year` LIKE %s;"
        query_params = (purchase_year,)

    return query, query_params


def build_create_query(bus_number,
                       year_purchased,
                       license_num,
                       bike_rack,
                       ada_lift):
    """
    Builds the query and query parameters for the add bus function
    for Buses.

    Returns the query and query parameters.

    Query is a SQL query.
    Query parameters is a tuple.
    """
    if license_num is None:
        query = ("INSERT INTO `Buses` "
                 "(`bus_number`, `purchase_year`, `bike_rack`, `ada_lift`) "
                 "VALUES (%s, %s, %s, %s);")
        query_params = (bus_number,
                        year_purchased,
                        bike_rack,
                        ada_lift)
    else:
        query = ("INSERT INTO `Buses` "
                 "(`bus_number`, `purchase_year`, `license`, `bike_rack`, `ada_lift`) "
                 "VALUES (%s, %s, %s, %s, %s);")
        query_params = (bus_number,
                        year_purchased,
                        license_num,
                        bike_rack,
                        ada_lift)

    return query, query_params


def build_update_query(updated_bus_num,
                       updated_purchase_year,
                       updated_license,
                       updated_bike_rack,
                       updated_ada_lift,
                       bus_id):
    """
    Builds the query and query parameters for the update bus function
    for Buses.

    Returns the query and query parameters.

    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = None
    params = None
    # A value of None for a required field means that no updated value will
    # be passed to the DB
    if updated_purchase_year and updated_license and not updated_bus_num:
        query = ("UPDATE `Buses` "
                 "SET `purchase_year`=%s, `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_purchase_year,
                  updated_license,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Only purchase_year is None
    if updated_bus_num and updated_license and not updated_purchase_year:
        query = ("UPDATE `Buses` "
                 "SET `bus_number`=%s, `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_bus_num,
                  updated_license,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Only license is None
    if updated_bus_num and updated_purchase_year and not updated_license:
        query = ("UPDATE `Buses` "
                 "SET `bus_number`=%s, `purchase_year`=%s, `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_bus_num,
                  updated_purchase_year,
                  None,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Bike_rack and ada_lift can't be None due the way the form works
    if not updated_bus_num and not updated_purchase_year and not updated_license:
        query = ("UPDATE `Buses` "
                 "SET `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (None,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Bus_num and purchase_year are None
    if updated_license and not updated_bus_num and not updated_purchase_year:
        query = ("UPDATE `Buses` "
                 "SET `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_license,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Bus_num and license are None
    if updated_purchase_year and not updated_bus_num and not updated_license:
        query = ("UPDATE `Buses` "
                 "SET `purchase_year`=%s, `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_purchase_year,
                  None,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # license and purchase_year are None
    if updated_bus_num and not updated_license and not updated_purchase_year:
        query = ("UPDATE `Buses` "
                 "SET `bus_number`=%s, `license`=%s, ``bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_bus_num,
                  None,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)
    # Nothing is None
    if updated_bus_num and updated_license and updated_purchase_year:
        query = ("UPDATE `Buses` "
                 "SET `bus_number`=%s, `purchase_year`=%s, `license`=%s, `bike_rack`=%s, `ada_lift`=%s "
                 "WHERE `bus_id`=%s;")
        params = (updated_bus_num,
                  updated_purchase_year,
                  updated_license,
                  updated_bike_rack,
                  updated_ada_lift,
                  bus_id)

    return query, params


# BUS ROUTES
@app.route("/buses", methods=["GET", "POST"])
@app.route("/buses/<error>", methods=["GET", "POST"])
def buses(error=None):
    bus_to_update = request.args.get("bus_to_update")
    bus_num_filter = None
    purchase_year_filter = None
    bus_license_filter = None

    # Create filters for searching
    if request.method == "POST" and "search-submit" in request.form.keys():
        try:
            bus_num_filter = (int(request.form.get("search_bus_number").strip())
                              if request.form.get("search_bus_number") else None)
            bus_license_filter = (str(request.form.get("search_bus_license").strip())
                                  if request.form.get("search_bus_license") else None)
            purchase_year_filter = (int(request.form.get("search_purchase_year").strip())
                                    if request.form.get("search_purchase_year") else None)
        except ValueError:
            error = "Incorrect data -- wrong type."
            return redirect(url_for("buses", error=error))

    elif request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("buses"))

    # Build query to populate update form
    select_query = ("SELECT * FROM `Buses` WHERE `bus_id`=%s;"
                    if bus_to_update else None)
    select_query_params = (bus_to_update,) if bus_to_update else None

    # Build query and query params
    query, query_params = build_search_query(bus_num_filter,
                                             purchase_year_filter,
                                             bus_license_filter)

    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested bus records. Try again!"
                cur.execute("SELECT * FROM `Buses`;")
                results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                bus_to_update = cur.fetchall()

                if len(bus_to_update) < 1:
                    bus_to_update = None
                    error = "Something went wrong! The selected route was not found."
    except:
        error = "Unable to retrieve bus data!"

    print(results)
    # Pass query results to jinja template for use on buses page
    return render_template("buses.j2",
                           buses=results,
                           bus_to_update=bus_to_update,
                           error=error)


@app.route("/add-bus", methods=["GET", "POST"])
def add_bus():
    error = None
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            bus_number = (int(request.form.get("new_bus_number").strip())
                          if request.form.get("new_bus_number") else None)
            year_purchased = (int(request.form.get("new_purchase_year").strip())
                              if request.form.get("new_purchase_year") else None)
            if request.form.get("no-license"):
                license_num = None
            else:
                license_num = (str(request.form.get("new_license").strip()) if
                               request.form.get("new_license") else None)
            bike_rack = (int(request.form.get("new_bike_rack").strip())
                         if request.form.get("new_bike_rack") else None)
            ada_lift = (int(request.form.get("new_ada_lift").strip())
                        if request.form.get("new_ada_lift") else None)
        except ValueError:
            error = "Invalid data -- wrong type."
            return redirect(url_for("buses", error=error))

        # Check for required fields before sending to DB
        if bus_number is None or year_purchased is None:
            error = "Missing required data."
            return redirect(url_for("buses", error=error))

        # Build query and query parameters
        query, query_params = build_create_query(bus_number,
                                                 year_purchased,
                                                 license_num,
                                                 bike_rack,
                                                 ada_lift)

        try:
            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to add bus to database."

    return redirect(url_for("buses", error=error))


@app.route("/update-bus/<int:bus_id>", methods=["GET", "POST"])
def update_bus(bus_id):
    error = None
    if request.method == "POST" and "cancel-update" in request.form.keys():
        return redirect(url_for("buses"))
    elif request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            updated_bus_num = (int(request.form.get("up_bus_number").strip())
                               if request.form.get("up_bus_number") else None)
            updated_purchase_year = (int(request.form.get("up_purchase_year").strip())
                                     if request.form.get("up_purchase_year") else None)
            if request.form.get("remove-license"):
                updated_license = None
            else:
                updated_license = (str(request.form.get("up_license").strip())
                                   if request.form.get("up_license") else None)
            updated_bike_rack = (int(request.form.get("up_bike_rack").strip())
                                 if request.form.get("up_bike_rack") else None)
            updated_ada_lift = (int(request.form.get("up_ada_lift").strip())
                                if request.form.get("up_ada_lift") else None)
        except ValueError:
            error = "Incorrect data entered -- wrong type."
            return redirect(url_for("buses", error=error))

        # Build update query
        query, params = build_update_query(updated_bus_num,
                                           updated_purchase_year,
                                           updated_license,
                                           updated_bike_rack,
                                           updated_ada_lift,
                                           bus_id)
        try:
            # Execute query
            with db.connection.cursor() as cur:
                cur.execute(query, params)
                cur.connection.commit()
        except:
            error = "Unable to update record."

    # Updated bus information will be displayed in top table on buses page
    return redirect(url_for("buses", error=error))


@app.route("/delete-bus/<int:selected_bus_id>", methods=["GET", "POST"])
def delete_bus(selected_bus_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Buses` WHERE `bus_id`=%s;"
    query_params = (selected_bus_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected bus record."

    return redirect(url_for("buses", error=error))


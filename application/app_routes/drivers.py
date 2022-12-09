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
# Use of two route decorators for the drivers() route based on the Flask documentation:
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
def build_search_query(driver_last_filter, driver_phone_filter, driver_first_filter):
    """
    Builds the query and query parameters for the search function
    for Route_Stops.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = "SELECT * FROM `Drivers`;"  # Default query to select all drivers
    query_params = None                 # Default query does not need params

    if driver_last_filter and not driver_phone_filter and not driver_first_filter:
        driver_name_filter = "%" + driver_last_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `last_name` LIKE %s;"
        query_params = (driver_name_filter,)
    elif driver_phone_filter and not driver_last_filter and not driver_first_filter:
        query = "SELECT * FROM `Drivers` WHERE `phone_number`=%s;"
        query_params = (driver_phone_filter,)
    elif driver_last_filter and driver_phone_filter and not driver_first_filter:
        driver_name_filter = "%" + driver_last_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `last_name` LIKE %s AND `phone_number`=%s;"
        query_params = (driver_name_filter, driver_phone_filter)
    elif driver_first_filter and not driver_last_filter and not driver_phone_filter:
        driver_name_filter = "%" + driver_first_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `first_name` LIKE %s;"
        query_params = (driver_name_filter,)
    elif driver_first_filter and driver_last_filter and not driver_phone_filter:
        driver_last_filter = "%" + driver_last_filter + "%"
        driver_first_filter = "%" + driver_first_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `last_name` LIKE %s AND `first_name` LIKE %s;"
        query_params = (driver_last_filter, driver_first_filter)
    elif driver_first_filter and driver_phone_filter and not driver_last_filter:
        driver_name_filter = "%" + driver_first_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `first_name` LIKE %s AND `phone_number`=%s;"
        query_params = (driver_name_filter, driver_phone_filter)
    elif driver_first_filter and driver_last_filter and driver_phone_filter:
        driver_last_filter = "%" + driver_last_filter + "%"
        driver_first_filter = "%" + driver_first_filter + "%"
        query = "SELECT * FROM `Drivers` WHERE `last_name` LIKE %s AND `first_name` LIKE %s AND `phone_number`=%s;"
        query_params = (driver_last_filter, driver_first_filter, driver_phone_filter)

    return query, query_params


# DRIVERS ROUTES
@app.route("/drivers", methods=["GET", "POST"])
@app.route("/drivers/<error>", methods=["GET", "POST"])
def drivers(error=None):
    select_query = None
    select_query_params = None
    driver_to_update = request.args.get("driver_to_update")
    driver_last_filter = None
    driver_first_filter = None
    driver_phone_filter = None

    if request.method == "POST" and "search-submit" in request.form.keys():
        try:
            driver_last_filter = str(request.form.get("search_driver_last").strip()) if request.method == "POST" else None
            driver_first_filter = str(request.form.get("search_driver_first").strip())if request.method == "POST" else None
            driver_phone_filter = str(request.form.get("search_driver_phone").strip()) if request.method == "POST" else None
        except ValueError:
            error = "Incorrect data -- wrong type."
            return redirect(url_for("drivers", error=error))
    elif request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("drivers"))

    if driver_to_update:
        # Build query if a driver has been selected for updating
        # This will be used populate the update form with the correct info
        select_query = "SELECT * FROM `Drivers` WHERE `driver_id`=%s;"
        select_query_params = (driver_to_update,)

    query, query_params = build_search_query(driver_last_filter,
                                             driver_phone_filter,
                                             driver_first_filter)

    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested driver records. Try again!"
                cur.execute("SELECT * FROM `Drivers`;")
                results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                driver_to_update = cur.fetchall()

                if len(driver_to_update) < 1:
                    driver_to_update = None
                    error = "Something went wrong! The selected driver was not found."
    except:
        error = "Unable to retrieve driver data!"

    return render_template("drivers.j2",
                           drivers=results,
                           driver_to_update=driver_to_update,
                           error=error)


@app.route("/delete-driver/<int:selected_driver_id>", methods=["GET", "POST"])
def delete_driver(selected_driver_id):
    error = None
    # Build delete query
    query = "DELETE FROM `Drivers` WHERE `driver_id`=%s;"
    query_params = (selected_driver_id,)

    try:
        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()
    except:
        error = "Unable to delete the selected driver record."

    return redirect(url_for("drivers", error=error))


@app.route("/update-driver/<int:driver_id>", methods=["GET", "POST"])
def update_driver(driver_id):
    error = None
    query = None
    params = None
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            updated_first_name = (str(request.form.get("up_first_name").strip())
                               if request.form.get("up_first_name") else None)
            updated_last_name = (str(request.form.get("up_last_name").strip())
                                     if request.form.get("up_last_name") else None)
            updated_phone_number = (str(request.form.get("up_phone").strip())
                               if request.form.get("up_phone") else None)
            updated_start_date = (str(request.form.get("up_start_date").strip())
                                 if request.form.get("up_start_date") else None)
        except ValueError:
            # Currently debug information for step 4 draft. Will be changed
            # to provide feedback to user later in project
            error = "Incorrect data entered -- wrong type."
            return redirect(url_for("drivers", error=error))

        if updated_first_name and updated_last_name and updated_phone_number and updated_start_date:
            query = "UPDATE `Drivers` SET `first_name`=%s, `last_name`=%s, `phone_number`=%s, `start_date`=%s WHERE `driver_id`=%s;"
            params = (updated_first_name, updated_last_name, updated_phone_number, updated_start_date, driver_id)

        try:
            # Execute query
            with db.connection.cursor() as cur:
                cur.execute(query, params)
                cur.connection.commit()
        except:
            error = "Unable to update driver."

    # Updated driver information will be displayed in top table on drivers page
    return redirect(url_for("drivers", error=error))


@app.route("/add-driver", methods=["GET", "POST"])
def add_driver():
    error = None
    if request.method == "POST" and "cancel-update" in request.form.keys():
        return redirect(url_for("drivers"))
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            first_name = (str(request.form.get("new_first_name").strip())
                          if request.form.get("new_first_name") else None)
            last_name = (str(request.form.get("new_last_name").strip())
                              if request.form.get("new_last_name") else None)
            phone_number = (str(request.form.get("new_phone_number").strip())
                         if request.form.get("new_phone_number") else None)
            start_date = (str(request.form.get("new_start_date").strip())
                        if request.form.get("new_start_date") else None)
        except ValueError:
            # Currently debug information for step 4 draft. Will be changed
            # to provide feedback to user later in project
            error = "Invalid data -- wrong type."
            return redirect(url_for("drivers", error=error))

        query = "INSERT INTO `Drivers` (`first_name`, `last_name`, `phone_number`, `start_date`) VALUES (%s, %s, %s, %s);"
        query_params = (first_name, last_name, phone_number, start_date)

        try:
            with db.connection.cursor() as cur:
                cur.execute(query, query_params)
                cur.connection.commit()
        except:
            error = "Unable to add driver to database."

    return redirect(url_for("drivers", error=error))

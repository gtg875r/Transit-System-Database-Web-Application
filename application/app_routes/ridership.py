
import datetime

from flask import redirect, render_template, request, url_for
from flask import current_app as app
from application import db


# HELPER FUNCTIONS
def build_search_query(datetime_start=None, datetime_end=None):
    """
    Builds the query and query parameters for the search function
    for Ridership logs.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    # Default query to select all ridership logs
    query = "SELECT * FROM `Passenger_Ridership_Logs`;"
    # Default query does not need params
    query_params = None

    if datetime_start and not datetime_end:
        query = "SELECT * FROM `Passenger_Ridership_Logs` WHERE `log_datetime` >= %s;"
        query_params = (datetime_start,)
    elif datetime_start and datetime_end:
        query = "SELECT * FROM `Passenger_Ridership_Logs` WHERE `log_datetime` >= %s AND `log_datetime` <= %s;"
        query_params = (datetime_start, datetime_end)
    elif datetime_end and not datetime_start:
        query = "SELECT * FROM `Passenger_Ridership_Logs` WHERE `log_datetime` <= %s;"
        query_params = (datetime_end,)

    return query, query_params


def build_create_query(passenger_entry=None,
                       passenger_exit=None,
                       new_driver_id=None,
                       new_route_stop_id=None,
                       new_bus_id=None,
                       new_datetime=None):
    """
    Builds the query and query parameters for the add log function
    for Ridership.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = None
    query_params = None

    # If new_driver_id is None and new_route_stop_id is None and new_bus_id is None
    if not new_driver_id and not new_route_stop_id and not new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`)"
                 "VALUES (%s, %s, %s);")
        query_params = (passenger_entry, passenger_exit, new_datetime)
    # If new_driver_id and not route stop or bus
    elif new_driver_id and not new_route_stop_id and not new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `driver_id`)"
                 "VALUES (%s, %s, %s, %s);")
        query_params = (passenger_entry, passenger_exit, new_datetime, new_driver_id)
    elif new_driver_id and new_route_stop_id and not new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `driver_id`, `route_stops_id`)"  
                 "VALUES (%s, %s, %s, %s, %s);")
        query_params = (passenger_entry, passenger_exit, new_datetime, new_driver_id, new_route_stop_id)
    elif new_driver_id and not new_route_stop_id and new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `driver_id`, `bus_id`)"
                 "VALUES (%s, %s, %s, %s, %s);")
        query_params = (
        passenger_entry, passenger_exit, new_datetime, new_driver_id,
        new_bus_id)
    elif new_driver_id and new_route_stop_id and new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `driver_id`, `route_stops_id`, `bus_id`)"
                 "VALUES (%s, %s, %s, %s, %s, %s);")
        query_params = (
        passenger_entry, passenger_exit, new_datetime, new_driver_id,
        new_route_stop_id, new_bus_id)
    elif not new_driver_id and new_route_stop_id and not new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `route_stops_id`)"
                 "VALUES (%s, %s, %s, %s);")
        query_params = (
        passenger_entry, passenger_exit, new_datetime, new_route_stop_id)
    elif not new_driver_id and new_route_stop_id and new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `route_stops_id`, `bus_id`)"
                 "VALUES (%s, %s, %s, %s, %s);")
        query_params = (
        passenger_entry, passenger_exit, new_datetime, new_route_stop_id, new_bus_id)
    elif not new_driver_id and not new_route_stop_id and new_bus_id:
        query = ("INSERT INTO `Passenger_Ridership_Logs`"
                 "(`passenger_entry`, `passenger_exit`, `log_datetime`, `bus_id`)"
                 "VALUES (%s, %s, %s, %s);")
        query_params = (
        passenger_entry, passenger_exit, new_datetime, new_bus_id)

    return query, query_params


def build_update_query(passenger_entry,
                       passenger_exit,
                       up_driver_id,
                       up_route_stop_id,
                       up_bus_id,
                       up_datetime,
                       log_id):
    """
    Builds the query and query parameters for the update log function
    for Ridership.
    Returns the query and query parameters.
    Query is a SQL query.
    Query parameters is a tuple.
    """
    query = None
    params = None
    # Only passenger_entry is None
    # Some of this structure is based off the example in the
    # OSU Flask starter code (cited at top of file)

    # Due to extensive use of dropdown menus, the only None value that could
    # mean the user does not have an update to the field is the datetime field.
    # All other None values would specifically insert a NULL value into the
    # db.
    if not up_datetime:
        query = ("UPDATE `Passenger_Ridership_Logs` "
                 "SET `passenger_entry`=%s, `passenger_exit`=%s, `driver_id`=%s, `route_stops_id`=%s, `bus_id`=%s "
                 "WHERE `log_id`=%s;")
        params = (passenger_entry, passenger_exit, up_driver_id, up_route_stop_id, up_bus_id, log_id)
    else:
        query = ("UPDATE `Passenger_Ridership_Logs` "
                 "SET `passenger_entry`=%s, `passenger_exit`=%s, `driver_id`=%s, `route_stops_id`=%s, `bus_id`=%s, `log_datetime`=%s "
                 "WHERE `log_id`=%s;")
        params = (passenger_entry, passenger_exit, up_driver_id, up_route_stop_id, up_bus_id, up_datetime, log_id)

    return query, params


# RIDERSHIP LOGS
@app.route("/ridership", methods=["GET", "POST"])
def ridership():
    # Use of request.args is based on:
    # Flask. (Nov. 10, 2022) class flask.Request in "Incoming Request Data" in
    # "API". [Flask v.2.2.x documentation].
    # https://flask.palletsprojects.com/en/2.2.x/api/#flask.Request
    error = None
    log_to_update = int(request.args.get("log_to_update")) if request.args.get("log_to_update") else None
    log_datetime_start = None
    log_datetime_end = None

    if request.method == "POST" and "search-clear" in request.form.keys():
        return redirect(url_for("ridership"))
    elif request.method == "POST" and (request.form.get("start_range_date") or request.form.get("end_range_date")):
        log_datetime_start = (datetime.datetime.fromisoformat(request.form.get("start_range_date").strip())
                              if request.form.get("start_range_date") else None)
        # Add seconds to make end date extend to the last second of the selected day
        # Otherwise a datetime greater than the first second of the day will be excluded from search results
        datetime_end = ((request.form.get("end_range_date").strip() + "T23:59:59")
                        if request.form.get("end_range_date") else None)
        log_datetime_end = (datetime.datetime.fromisoformat(datetime_end)
                            if datetime_end else None)

    select_query = ("SELECT * FROM `Passenger_Ridership_Logs` "
                    "WHERE `log_id`=%s;"
                    if log_to_update else None)
    select_query_params = (log_to_update,) if log_to_update else None

    # Build query and query params
    query, query_params = build_search_query(log_datetime_start, log_datetime_end)

    # Execute the query and fetch results based on
    # the example in the OSU Flask starter code:
    # gkochera. (Oct. 24, 2022) "Flask Starter App" [OSU CS340 Guide and
    # starter code]. https://github.com/osu-cs340-ecampus/flask-starter-app
    try:
        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            results = cur.fetchall()

            if len(results) < 1:
                error = "Unable to find requested log. Try again!"
                cur.execute("SELECT * FROM `Passenger_Ridership_Logs`;")
                results = cur.fetchall()

            # Retrieve all drivers for dropdown menu use
            query = "SELECT `driver_id`, `first_name`, `last_name` FROM `Drivers`;"
            cur.execute(query)
            driver_results = cur.fetchall()

            # Retrieve all route_stops for dropdown menu use
            query = ("SELECT DISTINCT `route_stops_id`, Transit_Routes.route_name "
                     "AS route_name, Bus_Stops.stop_name AS stop_name "
                     "FROM `Route_Stops` "
                     "JOIN `Transit_Routes` "
                     "ON Route_Stops.route_id = Transit_Routes.route_id "
                     "JOIN `Bus_Stops` "
                     "ON Route_Stops.stop_id = Bus_Stops.stop_id;")
            cur.execute(query)
            route_stop_results = cur.fetchall()

            # Retrieve all buses for dropdown menu use
            query = "SELECT `bus_id`, `bus_number` FROM `Buses`;"
            cur.execute(query)
            bus_results = cur.fetchall()

            if select_query:
                cur.execute(select_query, select_query_params)
                log_to_update = cur.fetchall()

                if len(log_to_update) < 1:
                    log_to_update = None
                    error = "Something went wrong! The selected log was not found."

            if log_to_update:
                for log_dict in log_to_update:
                    orig_datetime = log_dict['log_datetime']
                    formatted_datetime = datetime.datetime.isoformat(orig_datetime)
                    log_dict['log_datetime'] = formatted_datetime
    except:
        error = "Unable to retrieve passenger ridership logs!"

    # Pass query results to jinja template for use on buses page
    return render_template("ridership.j2",
                           logs=results,
                           drivers=driver_results,
                           route_stops=route_stop_results,
                           buses=bus_results,
                           log_to_update=log_to_update,
                           error=error)


@app.route("/add-log", methods=["GET", "POST"])
def add_log():
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            passenger_entry = (int(request.form.get("new_passenger_entry"))
                               if request.form.get("new_passenger_entry") else None)
            passenger_exit = (int(request.form.get("new_passenger_exit"))
                              if request.form.get("new_passenger_exit") else None)
            new_driver_id = (int(request.form.get("new_driver"))
                             if request.form.get("new_driver") else None)
            new_route_stop_id = (int(request.form.get("new_route"))
                                 if request.form.get("new_route") else None)
            new_bus_id = (int(request.form.get("new_bus"))
                          if request.form.get("new_bus") else None)
            # new_datetime = (" ".join(request.form.get("new_log_datetime").split("T"))
            #                 if request.form.get("new_log_datetime") else None)
            new_datetime = (datetime.datetime.fromisoformat(request.form.get("new_log_datetime"))
                            if request.form.get("new_log_datetime") else None)
        except ValueError:
            # Currently debug information for step 4 draft. Will be changed
            # to provide feedback to user later in project
            print("Invalid data -- wrong type.")
            return redirect(url_for("buses"))

        # Check for required fields before sending to DB
        if passenger_exit is None or passenger_entry is None or new_datetime is None:
            # Currently debug information for step 4 draft. Will be changed
            # to provide feedback to user later in project
            print("Missing required data.")
            return redirect(url_for("ridership"))

        # Build query and query parameters
        # Some of this structure is based off the example in the
        # OSU Flask starter code (cited at top of file)
        query, query_params = build_create_query(passenger_entry,
                                                 passenger_exit,
                                                 new_driver_id,
                                                 new_route_stop_id,
                                                 new_bus_id,
                                                 new_datetime)

        with db.connection.cursor() as cur:
            cur.execute(query, query_params)
            cur.connection.commit()

    return redirect(url_for("ridership"))


@app.route("/update-log/<int:log_id>", methods=["GET", "POST"])
def update_log(log_id):
    if request.method == "POST":
        # Cast to correct data types to ensure data is as expected
        try:
            passenger_entry = (int(request.form.get("up_passenger_entry"))
                               if request.form.get("up_passenger_entry") else None)
            passenger_exit = (int(request.form.get("up_passenger_exit"))
                              if request.form.get("up_passenger_exit") else None)
            up_driver_id = (int(request.form.get("up_driver"))
                            if request.form.get("up_driver") else None)
            up_route_stop_id = (int(request.form.get("up_route"))
                                if request.form.get("up_route") else None)
            up_bus_id = (int(request.form.get("up_bus"))
                         if request.form.get("up_bus") else None)
            up_datetime = (" ".join(request.form.get("up_log_datetime").split("T"))
                           if request.form.get("up_log_datetime") else None)
        except ValueError:
            # Currently debug information for step 4 draft. Will be changed
            # to provide feedback to user later in project
            print("Incorrect data entered -- wrong type.")
            return redirect(url_for("buses"))

        up_driver_id = None if up_driver_id == "None" else up_driver_id
        up_route_stop_id = None if up_route_stop_id == "None" else up_route_stop_id
        up_bus_id = None if up_bus_id == "None" else up_bus_id

        # Build update query
        query, params = build_update_query(passenger_entry,
                                           passenger_exit,
                                           up_driver_id,
                                           up_route_stop_id,
                                           up_bus_id,
                                           up_datetime,
                                           log_id)

        # Execute query
        with db.connection.cursor() as cur:
            cur.execute(query, params)
            cur.connection.commit()

    # Updated ridership log information will be displayed in top table on ridership page
    return redirect(url_for("ridership"))


@app.route("/delete-log/<int:selected_log_id>", methods=["GET", "POST"])
def delete_log(selected_log_id):
    # Build delete query
    query = "DELETE FROM `Passenger_Ridership_Logs` WHERE `log_id`=%s;"
    query_params = (selected_log_id,)

    # Execute query
    with db.connection.cursor() as cur:
        cur.execute(query, query_params)
        cur.connection.commit()

    return redirect(url_for("ridership"))
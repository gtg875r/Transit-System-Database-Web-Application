
-- Group 62: SQL: The Final Revenge
-- Team Members: Aaron Fowler and Julia Loy
-- Project Step 2

SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
SET AUTOCOMMIT=0;

CREATE OR REPLACE TABLE Drivers (
    driver_id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone_number CHAR(12) NOT NULL,
    start_date DATE NOT NULL,
    PRIMARY KEY (driver_id)
);

CREATE OR REPLACE TABLE Transit_Routes (
    route_id INT NOT NULL AUTO_INCREMENT,
    route_name VARCHAR(255) NOT NULL UNIQUE,
    route_color VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (route_id)
);

CREATE OR REPLACE TABLE Bus_Stops (
    stop_id INT NOT NULL AUTO_INCREMENT,
    stop_name VARCHAR(255) NOT NULL UNIQUE,
    bus_shelter TINYINT(1) NOT NULL,
    bench TINYINT(1) NOT NULL,
    trash TINYINT(1) NOT NULL,
    stop_latitude DECIMAL(7,5) NOT NULL,
    stop_longitude DECIMAL(8,5) NOT NULL,
    PRIMARY KEY (stop_id)
);

CREATE OR REPLACE TABLE Buses (
    bus_id INT NOT NULL AUTO_INCREMENT,
    bus_number INT NOT NULL UNIQUE,
    purchase_year INT NOT NULL,
    license VARCHAR(10) UNIQUE,
    bike_rack TINYINT(1) NOT NULL,
    ada_lift TINYINT(1) NOT NULL,
    PRIMARY KEY (bus_id)
);

-- Create intersection table for Drivers and Transit_Routes
CREATE OR REPLACE TABLE Driver_Routes (
    driver_routes_id INT NOT NULL AUTO_INCREMENT,
    driver_id INT NOT NULL,
    route_id INT NOT NULL,
    PRIMARY KEY (driver_routes_id),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
    ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES Transit_Routes(route_id)
    ON DELETE CASCADE
);

-- Create intersection table for Transit_Routes and Bus_Stops
CREATE OR REPLACE TABLE Route_Stops (
    route_stops_id INT NOT NULL AUTO_INCREMENT,
    route_id INT NOT NULL,
    stop_id INT NOT NULL,
    PRIMARY KEY (route_stops_id),
    FOREIGN KEY (route_id) REFERENCES Transit_Routes(route_id)
    ON DELETE CASCADE,
    FOREIGN KEY (stop_id) REFERENCES Bus_Stops(stop_id)
    ON DELETE CASCADE
);

CREATE OR REPLACE TABLE Passenger_Ridership_Logs (
    log_id INT NOT NULL AUTO_INCREMENT,
    passenger_entry TINYINT(1) NOT NULL,
    passenger_exit TINYINT(1) NOT NULL,
    log_datetime DATETIME NOT NULL,
    driver_id INT,
    route_stops_id INT,
    bus_id INT,
    PRIMARY KEY (log_id),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id) ON DELETE SET NULL,
    FOREIGN KEY (route_stops_id) REFERENCES Route_Stops(route_stops_id) ON DELETE SET NULL,
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id) ON DELETE SET NULL
);


INSERT INTO Drivers (first_name, last_name, phone_number, start_date)
VALUES ('Jimmy', 'Smith', '555-555-0001', '2010-10-31'),
('Rhonda', 'Alvarez', '555-555-0002', '2017-07-15'),
('Felicia', 'Jeffrey', '555-555-0003', '2020-03-15'),
('Rod', 'Washington', '555-555-0004', '2022-01-03');

INSERT INTO Transit_Routes (route_name, route_color)
VALUES ('Plaza Point', 'Gold'),
('Main Street', 'Blue'),
('Grant Park', 'Red'),
('Downtown', 'Green');

INSERT INTO Bus_Stops (stop_name, bus_shelter, bench, trash, stop_latitude, stop_longitude)
VALUES ('Ferst & Main St', 0, 0, 0, 33.77852, -84.40099),
('Ferst & Hickory St', 1, 0, 0, 33.77830, -84.39906),
('Ferst & Pine St', 1, 1, 1, 33.77769, -84.39575),
('Mercury & Main St', 0, 1, 0, 33.77693, -84.39375);

INSERT INTO Buses (bus_number, purchase_year, license, bike_rack, ada_lift)
VALUES (2201, 2022, 'GV5012', 1, 1),
(2003, 2020, 'GV5013', 0, 1),
(1917, 2019, 'GV5014', 1, 1),
(2202, 2022, NULL, 1, 1);

INSERT INTO Driver_Routes (driver_id, route_id)
VALUES (
    (SELECT driver_id FROM Drivers WHERE first_name = 'Jimmy' AND last_name = 'Smith'),
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Grant Park')
),
(
    (SELECT driver_id FROM Drivers WHERE first_name = 'Jimmy' AND last_name = 'Smith'),
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Downtown')
),
(
    (SELECT driver_id FROM Drivers WHERE first_name = 'Rhonda' AND last_name = 'Alvarez'),
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Plaza Point')
),
(
    (SELECT driver_id FROM Drivers WHERE first_name = 'Felicia' AND last_name = 'Jeffrey'),
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Main Street')
);

INSERT INTO Route_Stops (route_id, stop_id)
VALUES (
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Grant Park'),
    (SELECT stop_id FROM Bus_Stops WHERE stop_name = 'Ferst & Main St')
),
(
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Grant Park'),
    (SELECT stop_id FROM Bus_Stops WHERE stop_name = 'Ferst & Hickory St')
),
(
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Grant Park'),
    (SELECT stop_id FROM Bus_Stops WHERE stop_name = 'Ferst & Pine St')
),
(
    (SELECT route_id FROM Transit_Routes WHERE route_name = 'Main Street'),
    (SELECT stop_id FROM Bus_Stops WHERE stop_name = 'Mercury & Main St')
);

INSERT INTO Passenger_Ridership_Logs (passenger_entry, passenger_exit, driver_id, route_stops_id, bus_id, log_datetime)
VALUES (
    1,
    0,
    (SELECT driver_id FROM Drivers WHERE first_name = 'Jimmy' AND last_name = 'Smith'),
    (
      SELECT route_stops_id FROM Route_Stops JOIN Transit_Routes JOIN Bus_Stops
      WHERE Route_Stops.route_id = Transit_Routes.route_id
      AND Transit_Routes.route_name = 'Grant Park'
      AND Route_Stops.stop_id = Bus_Stops.stop_id
      AND Bus_Stops.stop_name = 'Ferst & Main St'
    ),
    (SELECT bus_id FROM Buses WHERE bus_number = '2003'),
    '2022-07-01 13:05:00'
),
(
    0,
    0,
    (SELECT driver_id FROM Drivers WHERE first_name = 'Jimmy' AND last_name = 'Smith'),
    (
      SELECT route_stops_id FROM Route_Stops JOIN Transit_Routes JOIN Bus_Stops
      WHERE Route_Stops.route_id = Transit_Routes.route_id
      AND Transit_Routes.route_name = 'Grant Park'
      AND Route_Stops.stop_id = Bus_Stops.stop_id
      AND Bus_Stops.stop_name = 'Ferst & Hickory St'
    ),
    (SELECT bus_id FROM Buses WHERE bus_number = '2003'),
    '2022-07-01 13:08:00'
),
(
    0,
    1,
    (SELECT driver_id FROM Drivers WHERE first_name = 'Jimmy' AND last_name = 'Smith'),
    (
      SELECT route_stops_id FROM Route_Stops JOIN Transit_Routes JOIN Bus_Stops
      WHERE Route_Stops.route_id = Transit_Routes.route_id
      AND Transit_Routes.route_name = 'Grant Park'
      AND Route_Stops.stop_id = Bus_Stops.stop_id
      AND Bus_Stops.stop_name = 'Ferst & Hickory St'
    ),
    (SELECT bus_id FROM Buses WHERE bus_number = '2003'),
    '2022-07-01 13:08:00'
),
(
    0,
    1,
    (SELECT driver_id FROM Drivers WHERE first_name = 'Felicia' AND last_name = 'Jeffrey'),
    (
      SELECT route_stops_id FROM Route_Stops JOIN Transit_Routes JOIN Bus_Stops
      WHERE Route_Stops.route_id = Transit_Routes.route_id
      AND Transit_Routes.route_name = 'Main Street'
      AND Route_Stops.stop_id = Bus_Stops.stop_id
      AND Bus_Stops.stop_name = 'Mercury & Main St'
    ),
    (SELECT bus_id FROM Buses WHERE bus_number = '1917'),
    '2022-07-05 14:15:00'
),
(
    1,
    0,
    (SELECT driver_id FROM Drivers WHERE first_name = 'Felicia' AND last_name = 'Jeffrey'),
    (
      SELECT route_stops_id FROM Route_Stops JOIN Transit_Routes JOIN Bus_Stops
      WHERE Route_Stops.route_id = Transit_Routes.route_id
      AND Transit_Routes.route_name = 'Main Street'
      AND Route_Stops.stop_id = Bus_Stops.stop_id
      AND Bus_Stops.stop_name = 'Mercury & Main St'
    ),
    (SELECT bus_id FROM Buses WHERE bus_number = '1917'),
    '2022-07-04 14:15:00'
);

SET FOREIGN_KEY_CHECKS=1;
SET UNIQUE_CHECKS=1;
COMMIT;

CREATE DATABASE IF NOT EXISTS notice_base;

USE notice_base;
# Create Users
# Officer Account
CREATE USER IF NOT EXISTS  'officer_user'@'localhost' IDENTIFIED BY 'officer_password';

# Person's ZIP Code
# Accepts both ZIP and ZIP+4 standards
CREATE TABLE reg_zip_code (
	zip_code VARCHAR(10) NOT NULL,
    state VARCHAR(40) NOT NULL,
    city VARCHAR(40) NOT NULL,
    
    PRIMARY KEY (zip_code)
);

# Entity's Registration Address
CREATE TABLE reg_address (
	address_id INT AUTO_INCREMENT NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    street VARCHAR(100) NOT NULL,
    house VARCHAR(20) NOT NULL,
    
    PRIMARY KEY (address_id),
    FOREIGN KEY (zip_code) REFERENCES reg_zip_code(zip_code) ON DELETE RESTRICT ON UPDATE RESTRICT
);

# Person's details from perspective of a Driver
CREATE TABLE driver_details (
	driver_id INT AUTO_INCREMENT NOT NULL,
    address_id INT NOT NULL, 
    email VARCHAR(60) NOT NULL, # New Field
    username VARCHAR(60) NOT NULL, # New Field
    user_password VARCHAR(70) NOT NULL, # New Field
    phone_number VARCHAR(15) NOT NULL, # New Field
    licence_number VARCHAR(20) NOT NULL,
    state_issue VARCHAR(40) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    height_inches INT NOT NULL,
    weight_pounds INT NOT NULL,
    eyes_colour VARCHAR(10) NOT NULL,
    
    PRIMARY KEY (driver_id),
    FOREIGN KEY (address_id) REFERENCES reg_address(address_id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    # Logical height range
    CHECK (height_inches >= 36 AND height_inches <= 96),
    
    # Logical weight range
    CHECK (weight_pounds >= 50 AND weight_pounds <= 500)
);

# Details of the car itself
CREATE TABLE car_details (
	car_id INT AUTO_INCREMENT NOT NULL,
    driver_id INT NOT NULL,
    address_id INT NOT NULL,
    licence_plate VARCHAR(20) NOT NULL,
    plate_state_issue VARCHAR(40) NOT NULL,
    vin VARCHAR(20) NOT NULL UNIQUE,
    colour VARCHAR(20) NOT NULL,
    make VARCHAR(40) NOT NULL,
    year_production YEAR NOT NULL,
    car_type VARCHAR(40) NOT NULL,
    
    PRIMARY KEY (car_id),
    FOREIGN KEY (driver_id) REFERENCES driver_details (driver_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES reg_address (address_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    
    # Car can't be from the future
    CHECK (year_production <= 2026),
    
    # Car must be reasonably old
    CHECK (year_production >= 1900)
);

# ZIP code of the violation
CREATE TABLE violation_zip_code(
	zip_code VARCHAR(10) NOT NULL,
    state VARCHAR(40) NOT NULL,
    city VARCHAR(40) NOT NULL,
    district VARCHAR(40) NOT NULL,
    
    PRIMARY KEY (zip_code)
);

# Address of the violation
CREATE TABLE violation_address(
	address_id INT AUTO_INCREMENT NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    street VARCHAR(100),
    
    PRIMARY KEY (address_id),
    FOREIGN KEY (zip_code) REFERENCES violation_zip_code (zip_code) ON DELETE RESTRICT ON UPDATE RESTRICT
);

# Details of notice
CREATE TABLE notice_info (
	notice_id VARCHAR(100) NOT NULL,
    car_id INT NOT NULL,
    address_id INT NOT NULL,
    violation_date_time DATETIME NOT NULL,
    detachment VARCHAR(20) NOT NULL,
    violation_severity ENUM('Low', 'Medium', 'High') NOT NULL,
    notice_status ENUM('Active', 'Resolved', 'Expired') NOT NULL,
    notification_sent BOOL NOT NULL,
    entry_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    violation_description VARCHAR(400) NOT NULL,
    
    PRIMARY KEY (notice_id),
    FOREIGN KEY (car_id) REFERENCES car_details (car_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES violation_address (address_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    
    # Logical checks
    # Date of expiry must be after entry (at least 1 day)
    CHECK (expiry_date > entry_date),
    
    # Entry date should not be before violation date
    CHECK (entry_date >= DATE(violation_date_time))
);

# Officer's details
CREATE TABLE officer_info (
	badge_number VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    
    PRIMARY KEY (badge_number)
);

# Actions taken by the officer in regards to the notice
CREATE TABLE actions (
	action_id VARCHAR(100) NOT NULL,
    notice_id VARCHAR(100) NOT NULL,
    badge_number VARCHAR(100) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    
    PRIMARY KEY (action_id),
    FOREIGN KEY (notice_id) REFERENCES notice_info (notice_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (badge_number) REFERENCES officer_info (badge_number) ON DELETE RESTRICT ON UPDATE RESTRICT
);

# Permissions
# Officer's Full Access
GRANT ALL PRIVILEGES ON notice_base.* TO 'officer_user'@'localhost';

# Commit Privileges
FLUSH PRIVILEGES;

# Populate tables with data
# Case 1
INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'10103', 'New York', 'New York'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'10103', 'Madison Avenue', '2A'
);

INSERT INTO driver_details (
    address_id, email, username, user_password, phone_number, licence_number, state_issue, last_name, first_name, dob,
    height_inches, weight_pounds, eyes_colour
)
VALUES (
    1, 'johndoe@gmail.com', 'john_doe', '007jd', '07455890052',
    'NY1234567', 'New York', 'Doe', 'John', '1990-05-29',
    72, 154, 'Blue'
);

INSERT INTO car_details (
    driver_id, address_id, licence_plate, plate_state_issue,
    vin, colour, make, year_production, car_type
)
VALUES (
    1, 1, 'ABC123', 'New York', '1ABCD82633A004352', 'Blue',
    'Ford', 1962, 'Sedan'
);

INSERT INTO violation_zip_code (
	zip_code, state, city, district
)
VALUES (
	'11201', 'New York', 'New York', 'Brooklyn'
);

INSERT INTO violation_address (
	zip_code, street
)
VALUES (
	'11201', 'First Avenue'
);

INSERT INTO notice_info (
	notice_id, car_id, address_id, violation_date_time, detachment, violation_severity, notice_status,
    notification_sent, entry_date, expiry_date, violation_description
)
VALUES (
	'N001', 1, 1, '2024-05-10 14:47:00', 'NYD-99', 'High', 'Active', TRUE, '2024-05-11', '2025-05-11',
    'Vehicle was parked in a no-parking area near First Avenue.'
);

INSERT INTO officer_info (
	badge_number, last_name, first_name
)
VALUES (
	'B001', 'Holt', 'Raymond'
);

INSERT INTO actions (
	action_id, notice_id, badge_number, action_type
)
VALUES (
	'A001', 'N001', 'B001', 'Warning'
);

# Case 2
INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'10104', 'New York', 'New York'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'10104', '103rd', '8C'
);

INSERT INTO driver_details (
    address_id, email, username, user_password, phone_number, licence_number, state_issue, last_name, first_name, dob,
    height_inches, weight_pounds, eyes_colour
)
VALUES (
    2, 'kevnicks@gmail.com', 'kevnicks', '0098', '08988763321', 'NY2234567', 'New York', 'Nicholas', 'Kevin', '1963-11-22',
    70, 180, 'Green'
);

INSERT INTO car_details (
    driver_id, address_id, licence_plate, plate_state_issue,
    vin, colour, make, year_production, car_type
)
VALUES (
    2, 2, 'ABC223', 'New York', '1ABCD12633B004352', 'Red',
    'Dodge', 1970, 'Sedan'
);

INSERT INTO violation_zip_code (
	zip_code, state, city, district
)
VALUES (
	'11301', 'New York', 'New York', 'Queens'
);

INSERT INTO violation_address (
	zip_code, street
)
VALUES (
	'11301', 'Nights Boulevard'
);

INSERT INTO notice_info (
	notice_id, car_id, address_id, violation_date_time, detachment, violation_severity, notice_status,
    notification_sent, entry_date, expiry_date, violation_description
)
VALUES (
	'N002', 2, 2, '2023-05-10 12:47:00', 'NYD-99', 'Low', 'Active', TRUE, '2023-05-11', '2024-05-11',
    'Vehicle sped up by additional 5 miles an hour'
);

INSERT INTO actions (
	action_id, notice_id, badge_number, action_type
)
VALUES (
	'A002', 'N002', 'B001', 'Warning'
);

# Case 3
INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'10124', 'New York', 'New York'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'10124', '83rd', '905A'
);

INSERT INTO driver_details (
    address_id, email, username, user_password, phone_number, licence_number, state_issue, last_name, first_name, dob,
    height_inches, weight_pounds, eyes_colour
)
VALUES (
    3, 'lmich@outlook.com', 'l_michs', '909009LM', '093833891183', 'NY2334567',
    'New York', 'Michaels', 'Larry', '2000-08-22',
    63, 130, 'Brown'
);

INSERT INTO car_details (
    driver_id, address_id, licence_plate, plate_state_issue,
    vin, colour, make, year_production, car_type
)
VALUES (
    3, 3, 'ABC222', 'New York', '1BBCD12633B004352', 'Navy',
    'Mercedes', 2011, 'Sedan'
);

INSERT INTO violation_zip_code (
	zip_code, state, city, district
)
VALUES (
	'11321', 'New York', 'New York', 'Queens'
);

INSERT INTO violation_address (
	zip_code, street
)
VALUES (
	'11321', 'Knights Boulevard'
);

INSERT INTO notice_info (
	notice_id, car_id, address_id, violation_date_time, detachment, violation_severity, notice_status,
    notification_sent, entry_date, expiry_date, violation_description
)
VALUES (
	'N003', 3, 3, '2025-02-20 03:20:00', 'NYD-12', 'High', 'Active', TRUE, '2025-02-20', '2026-02-20',
    'Drunken driving.'
);

INSERT INTO officer_info (
	badge_number, last_name, first_name
)
VALUES (
	'B002', 'Draper', 'Jacob'
);

INSERT INTO actions (
	action_id, notice_id, badge_number, action_type
)
VALUES (
	'A003', 'N003', 'B002', 'Fine'
);

# Case 4
INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'90001', 'California', 'Los Angeles'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'90001', '83rd', '905A'
);

INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'20124', 'New York', 'New York'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'20124', '83rd', '55A'
);

INSERT INTO driver_details (
    address_id, email, username, user_password, phone_number, licence_number, state_issue, last_name, first_name, dob,
    height_inches, weight_pounds, eyes_colour
)
VALUES (
    4, 'samsamail@gmail.com', 'bugger', 'sam0987', '73736353635',
    'CA2334567', 'California', 'Samsa', 'Gregor', '1970-09-22',
    69, 153, 'Blue'
);

INSERT INTO car_details (
    driver_id, address_id, licence_plate, plate_state_issue,
    vin, colour, make, year_production, car_type
)
VALUES (
    4, 5, 'ABC232', 'New York', '1BCCD12633B004352', 'Black',
    'Jeep', 2011, 'Truck'
);

INSERT INTO violation_zip_code (
	zip_code, state, city, district
)
VALUES (
	'10001', 'New York', 'New York', 'Chelsea'
);

INSERT INTO violation_address (
	zip_code, street
)
VALUES (
	'10001', 'Chelsea Lane'
);

INSERT INTO notice_info (
	notice_id, car_id, address_id, violation_date_time, detachment, violation_severity, notice_status,
    notification_sent, entry_date, expiry_date, violation_description
)
VALUES (
	'N004', 4, 4, '2025-02-20 01:00:00', 'NYD-12', 'High', 'Active', TRUE, '2025-02-20', '2026-02-20',
    'Speeding in a 30mph zone by 20 miles'
);

INSERT INTO officer_info (
	badge_number, last_name, first_name
)
VALUES (
	'B003', 'Peralta', 'Jacob'
);

INSERT INTO actions (
	action_id, notice_id, badge_number, action_type
)
VALUES (
	'A004', 'N004', 'B003', 'Fine'
);

# Case 5
INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'07001', 'New Jersey', 'Princeton'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'07001', '84th', '1A'
);

INSERT INTO reg_zip_code (
zip_code, state, city
)
VALUES (
	'10125', 'New York', 'New York'
);

INSERT INTO reg_address (
	zip_code, street, house
)
VALUES (
	'10125', '83rd', '55A'
);

INSERT INTO driver_details (
    address_id, email, username, user_password, phone_number, licence_number, state_issue, last_name, first_name, dob,
    height_inches, weight_pounds, eyes_colour
)
VALUES (
    5, 'myemail@gmail.com', 'beetle', 'franzkafka', '08000372282',
    'NJ2334567', 'New Jersey', 'Samsa', 'Gregor', '1970-09-22',
    69, 153, 'Blue'
);

INSERT INTO car_details (
    driver_id, address_id, licence_plate, plate_state_issue,
    vin, colour, make, year_production, car_type
)
VALUES (
    5, 6, 'ABC232', 'New York', '1BCCA12633B004352', 'Black',
    'Ford', 2020, 'Truck'
);

INSERT INTO violation_zip_code (
	zip_code, state, city, district
)
VALUES (
	'10002', 'New York', 'New York', 'Chelsea'
);

INSERT INTO violation_address (
	zip_code, street
)
VALUES (
	'10002', 'Chelsea Lane 2'
);

INSERT INTO notice_info (
	notice_id, car_id, address_id, violation_date_time, detachment, violation_severity, notice_status,
    notification_sent, entry_date, expiry_date, violation_description
)
VALUES (
	'N005', 5, 5, '2025-08-10 10:00:00', 'NYD-19', 'Low', 'Active', TRUE, '2025-08-10', '2026-08-10',
    'Speeding by 1mph in a 30mph zone.'
);

INSERT INTO actions (
	action_id, notice_id, badge_number, action_type
)
VALUES (
	'A005', 'N005', 'B003', 'Warning'
);
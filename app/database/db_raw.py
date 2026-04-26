# app/database/db_raw.py
# Imports
import MySQLdb

# Get Connection
def get_connection():
    # Define Connection Parameters
    conn = MySQLdb.connect(
        host = "localhost",
        port = 3306,
        user = "root",
        password = "0777",
        db = "notice_base",
        charset="utf8mb4"
    )

    return conn

"""GET"""

# Get Civilian Account by Username or Email
def fetch_civilian_by_login(login: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT driver_id, address_id, email, username, user_password, phone_number,
           licence_number, state_issue, last_name, first_name, dob,
           height_inches, weight_pounds, eyes_colour
    FROM driver_details
    WHERE username = %s OR email = %s
    """

    cursor.execute(query, (login, login))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

# Check if Civilian Login Details Are Already Registered
def civilian_account_exists(username: str, email: str, licence_number: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT username, email, licence_number
    FROM driver_details
    WHERE username = %s OR email = %s OR licence_number = %s
    """

    cursor.execute(query, (username, email, licence_number))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

# Get Driver's Details by ID
def fetch_driver_details(driver_id: int):
    # Open SQL Connection
    conn = get_connection()
    cursor = conn.cursor()

    # SQL Query
    query = """SELECT *
    FROM driver_details
    WHERE driver_id = %s;
    """

    # Execute Query
    cursor.execute(query, (driver_id,))
    row = cursor.fetchone()

    # Close Connection
    cursor.close()
    conn.close()

    # Output Results
    return row

# Get Notices Based on the Driver's ID
def fetch_driver_notices(driver_id: int):
    # Open SQL Bridge
    conn = get_connection()
    cursor = conn.cursor()

    # SQL Query
    """
        Extracts the notice details based solely
        on the driver's ID. The normalisation indirectly
        links the driver's ID and notice ID field through
        the car's ID, since the notices are directly
        written on cars and inherited to the owner.
    """

    query = """
    SELECT
        notice_info.notice_id,
        notice_info.violation_date_time,
        notice_info.detachment,
        notice_info.violation_severity,
        notice_info.notice_status,
        notice_info.notification_sent,
        notice_info.entry_date,
        notice_info.expiry_date,
        notice_info.violation_description,
        CONCAT(
            car_details.year_production,
            ' ',
            car_details.make,
            ' ',
            car_details.car_type,
            ' (',
            car_details.licence_plate,
            ')'
        ) AS car,
        CONCAT(
            violation_address.street,
            ', ',
            violation_zip_code.city,
            ', ',
            violation_zip_code.state,
            ' ',
            violation_zip_code.zip_code
        ) AS address
    FROM notice_info
    JOIN car_details ON notice_info.car_id = car_details.car_id
    JOIN violation_address ON notice_info.address_id = violation_address.address_id
    JOIN violation_zip_code ON violation_address.zip_code = violation_zip_code.zip_code
    WHERE car_details.driver_id = %s
    ORDER BY notice_info.violation_date_time DESC
    """

    # Execute Query
    cursor.execute(query, (driver_id,))
    rows = cursor.fetchall()

    # Close Connection
    cursor.close()
    conn.close()

    # Output Results
    return rows

# Get All Drivers
def fetch_all_drivers():
    # Open an SQL Bridge
    conn = get_connection()
    cursor = conn.cursor()

    # Query
    query = """
    SELECT *
    FROM driver_details
    """

    # Execute Query
    cursor.execute(query)
    row = cursor.fetchall()

    # Close Connection
    cursor.close()
    conn.close()

    # Output Results
    return row

"""POST"""

# Register a New Civilian Driver Account
def create_civilian_account(civilian, hashed_password: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM reg_zip_code WHERE zip_code = %s",
            (civilian.address.zip_code,)
        )

        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO reg_zip_code (zip_code, state, city)
                VALUES (%s, %s, %s)
                """,
                (
                    civilian.address.zip_code,
                    civilian.address.state,
                    civilian.address.city
                )
            )

        cursor.execute(
            """
            INSERT INTO reg_address (zip_code, street, house)
            VALUES (%s, %s, %s)
            """,
            (
                civilian.address.zip_code,
                civilian.address.street,
                civilian.address.house
            )
        )

        address_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO driver_details (
                address_id,
                email,
                username,
                user_password,
                phone_number,
                licence_number,
                state_issue,
                last_name,
                first_name,
                dob,
                height_inches,
                weight_pounds,
                eyes_colour
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                address_id,
                civilian.email,
                civilian.username,
                hashed_password,
                civilian.phone_number,
                civilian.licence_number,
                civilian.state_issue,
                civilian.last_name,
                civilian.first_name,
                civilian.dob,
                civilian.height_inches,
                civilian.weight_pounds,
                civilian.eyes_colour
            )
        )

        driver_id = cursor.lastrowid
        conn.commit()

        return driver_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# Create a New Driver
def create_driver(driver, address):
    # Open SQL Connection
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # First, Check ZIP
        cursor.execute(
            "SELECT 1 FROM reg_zip_code WHERE zip_code = %s",
            (address.zip_code,)
        )

        # Then, If the ZIP doesn't exist, we can insert it
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO reg_zip_code (zip_code, state, city)
                VALUES (%s, %s, %s)
                """,
                (address.zip_code, address.state, address.city)
            )

        # Then, Insert Address
        cursor.execute(
            """
            INSERT INTO reg_address (zip_code, street, house)
            VALUES (%s, %s, %s)
            """,
            (address.zip_code, address.street, address.house)
        )

        address_id = cursor.lastrowid

        # Then, Insert Driver After Previous Details Have Been Completed
        cursor.execute(
            """
            INSERT INTO driver_details (
                address_id,
                email,
                username,
                user_password,
                phone_number,
                licence_number,
                state_issue,
                last_name,
                first_name,
                dob,
                height_inches,
                weight_pounds,
                eyes_colour
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                address_id,
                driver.email,
                driver.username,
                driver.user_password,
                driver.phone_number,
                driver.licence_number,
                driver.state_issue,
                driver.last_name,
                driver.first_name,
                driver.dob,
                driver.height_inches,
                driver.weight_pounds,
                driver.eyes_colour
            )
        )

        driver_id = cursor.lastrowid
        conn.commit()
        
        return driver_id

    # In case things go south – roll back
    except Exception:
        conn.rollback()
        raise

    # Final Leg of the Journey
    finally:
        cursor.close()
        conn.close()

# Create a New Notice
def create_notice(notice, violation_zip, violation_address):
    # Open SQL Connection
    conn = get_connection()
    cursor = conn.cursor()

    # Main Leg
    try:
        # First, Check That The Car Exists
        cursor.execute(
            "SELECT 1 FROM car_details WHERE car_id = %s",
            (notice.car_id,)
        )

        # If Not, Throw Error
        if cursor.fetchone() is None:
            raise ValueError("Car does not exist. Cannot issue notice.")

        # Then, Check ZIP Code For Violation
        cursor.execute(
            "SELECT 1 FROM violation_zip_code WHERE zip_code = %s",
            (violation_zip.zip_code,)
        )

        # If ZIP doesn't exist, insert it
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO violation_zip_code (
                    zip_code,
                    state,
                    city,
                    district
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    violation_zip.zip_code,
                    violation_zip.state,
                    violation_zip.city,
                    violation_zip.district
                )
            )

        # Then, Insert Violation Address
        cursor.execute(
            """
            INSERT INTO violation_address (
                zip_code,
                street
            )
            VALUES (%s, %s)
            """,
            (
                violation_zip.zip_code,
                violation_address.street
            )
        )

        address_id = cursor.lastrowid

        # Finally, Insert Notice
        cursor.execute(
            """
            INSERT INTO notice_info (
                notice_id,
                car_id,
                address_id,
                violation_date_time,
                detachment,
                violation_severity,
                notice_status,
                notification_sent,
                entry_date,
                expiry_date,
                violation_description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                notice.notice_id,
                notice.car_id,
                address_id,
                notice.violation_date_time,
                notice.detachment,
                notice.violation_severity,
                notice.notice_status,
                notice.notification_sent,
                notice.entry_date,
                notice.expiry_date,
                notice.violation_description
            )
        )

        conn.commit()

        return notice.notice_id

    # In case things go south – roll back
    except Exception:
        conn.rollback()
        raise

    # Final Leg of the Journey
    finally:
        cursor.close()
        conn.close()

"""DELETE"""

# Delete Notice by ID
def delete_notice(notice_id: str):
    # Connect to the Database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # First, Check Notice Exists
        cursor.execute(
            "SELECT 1 FROM notice_info WHERE notice_id = %s",
            (notice_id,)
        )

        # Notice Not Found
        if cursor.fetchone() is None:
            return False 

        # Delete Dependent Legal Actions First
        cursor.execute(
            "DELETE FROM actions WHERE notice_id = %s",
            (notice_id,)
        )

        # Then Delete Notice Itself
        cursor.execute(
            "DELETE FROM notice_info WHERE notice_id = %s",
            (notice_id,)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# Delete Driver by ID
# Uses manual cascading
def delete_driver(driver_id: int):
    # Connect to SQL
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check Driver Exists
        cursor.execute(
            "SELECT address_id FROM driver_details WHERE driver_id = %s",
            (driver_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return False

        driver_address_id = result[0]

        # Get All car_ids Owned by This Driver
        cursor.execute(
            "SELECT car_id FROM car_details WHERE driver_id = %s",
            (driver_id,)
        )

        cars = cursor.fetchall()

        for car in cars:
            car_id = car[0]

            # Get All Notices For This Car
            cursor.execute(
                "SELECT notice_id FROM notice_info WHERE car_id = %s",
                (car_id,)
            )

            notices = cursor.fetchall()

            for notice in notices:
                notice_id = notice[0]

                # Delete Actions Linked to Notice
                cursor.execute(
                    "DELETE FROM actions WHERE notice_id = %s",
                    (notice_id,)
                )

                # Delete Notice
                cursor.execute(
                    "DELETE FROM notice_info WHERE notice_id = %s",
                    (notice_id,)
                )

            # Delete Car
            cursor.execute(
                "DELETE FROM car_details WHERE car_id = %s",
                (car_id,)
            )

        # Finally Delete Driver
        cursor.execute(
            "DELETE FROM driver_details WHERE driver_id = %s",
            (driver_id,)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

"""PUT"""

# Store a New Civilian Password Hash
def update_civilian_password(driver_id: int, hashed_password: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE driver_details
            SET user_password = %s
            WHERE driver_id = %s
            """,
            (hashed_password, driver_id)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# Update Driver (Full PUT) and return updated row
def update_driver(driver_id: int, payload):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check driver exists + get address_id
        cursor.execute(
            "SELECT address_id FROM driver_details WHERE driver_id = %s",
            (driver_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return None

        address_id = result[0]

        # Check ZIP exists
        cursor.execute(
            "SELECT 1 FROM reg_zip_code WHERE zip_code = %s",
            (payload.address.zip_code,)
        )

        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO reg_zip_code (zip_code, state, city)
                VALUES (%s, %s, %s)
                """,
                (
                    payload.address.zip_code,
                    payload.address.state,
                    payload.address.city
                )
            )

        # Update Address
        cursor.execute(
            """
            UPDATE reg_address
            SET zip_code = %s,
                street = %s,
                house = %s
            WHERE address_id = %s
            """,
            (
                payload.address.zip_code,
                payload.address.street,
                payload.address.house,
                address_id
            )
        )

        # Update Driver Details
        cursor.execute(
            """
            UPDATE driver_details
            SET 
                email = %s,
                username = %s,
                user_password = %s,
                phone_number = %s,
                licence_number = %s,
                state_issue = %s,
                last_name = %s,
                first_name = %s,
                dob = %s,
                height_inches = %s,
                weight_pounds = %s,
                eyes_colour = %s
            WHERE driver_id = %s
            """,
            (
                payload.email,
                payload.username,
                payload.user_password,
                payload.phone_number,
                payload.licence_number,
                payload.state_issue,
                payload.last_name,
                payload.first_name,
                payload.dob,
                payload.height_inches,
                payload.weight_pounds,
                payload.eyes_colour,
                driver_id
            )
        )

        conn.commit()

        # Return Updated Row
        cursor.execute(
            """
            SELECT driver_id, address_id, email, username, user_password, phone_number,
                    licence_number, state_issue, last_name, first_name, dob,
                    height_inches, weight_pounds, eyes_colour
            FROM driver_details
            WHERE driver_id = %s
            """,
            (driver_id,)
        )

        return cursor.fetchone()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# Update Notice and Return Updated Row
def update_notice(notice_id: str, payload):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check notice exists + get address_id
        cursor.execute(
            "SELECT address_id FROM notice_info WHERE notice_id = %s",
            (notice_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return None

        address_id = result[0]

        # Check violation ZIP exists
        cursor.execute(
            "SELECT 1 FROM violation_zip_code WHERE zip_code = %s",
            (payload.violation_zip.zip_code,)
        )

        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO violation_zip_code (zip_code, state, city, district)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    payload.violation_zip.zip_code,
                    payload.violation_zip.state,
                    payload.violation_zip.city,
                    payload.violation_zip.district
                )
            )

        # Update violation address
        cursor.execute(
            """
            UPDATE violation_address
            SET zip_code = %s,
                street = %s
            WHERE address_id = %s
            """,
            (
                payload.violation_zip.zip_code,
                payload.violation_address.street,
                address_id
            )
        )

        # Update notice_info
        cursor.execute(
            """
            UPDATE notice_info
            SET car_id = %s,
                violation_date_time = %s,
                detachment = %s,
                violation_severity = %s,
                notice_status = %s,
                notification_sent = %s,
                entry_date = %s,
                expiry_date = %s,
                violation_description = %s
            WHERE notice_id = %s
            """,
            (
                payload.car_id,
                payload.violation_date_time,
                payload.detachment,
                payload.violation_severity,
                payload.notice_status,
                payload.notification_sent,
                payload.entry_date,
                payload.expiry_date,
                payload.violation_description,
                notice_id
            )
        )

        conn.commit()

        # Return updated row
        cursor.execute(
            """
            SELECT notice_id, violation_date_time, detachment,
                   violation_severity, notice_status,
                   notification_sent, entry_date,
                   expiry_date, violation_description
            FROM notice_info
            WHERE notice_id = %s
            """,
            (notice_id,)
        )

        return cursor.fetchone()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

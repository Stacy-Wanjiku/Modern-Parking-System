# ============================================================
#              PARKING SYSTEM DATABASE
# ============================================================

import sqlite3


# Name of our database file
DATABASE = "parking.db"


# Total number of parking slots
TOTAL_SLOTS = 50


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():

    connection = sqlite3.connect(DATABASE)

    # Allows us to access columns using their names
    connection.row_factory = sqlite3.Row

    return connection


# ------------------------------------------------------------
# INITIALIZE DATABASE
# ------------------------------------------------------------

def initialize_database():

    connection = get_connection()


    # Create vehicles table if it does not already exist
    connection.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            registration TEXT UNIQUE NOT NULL,

            arrival_time TEXT NOT NULL,

            parking_slot INTEGER NOT NULL
        )
    """)


    connection.commit()

    connection.close()


# ------------------------------------------------------------
# GET AVAILABLE PARKING SLOTS
# ------------------------------------------------------------

def get_available_slots():

    connection = get_connection()


    # Count the number of vehicles currently parked
    occupied = connection.execute(
        "SELECT COUNT(*) FROM vehicles"
    ).fetchone()[0]


    connection.close()


    # Available = Total - Occupied
    return TOTAL_SLOTS - occupied


# ------------------------------------------------------------
# FIND NEXT AVAILABLE SLOT
# ------------------------------------------------------------

def get_next_available_slot():

    connection = get_connection()


    # Get all occupied parking slots
    rows = connection.execute(
        "SELECT parking_slot FROM vehicles"
    ).fetchall()


    connection.close()


    # Store occupied slots in a set
    occupied_slots = {
        row["parking_slot"]
        for row in rows
    }


    # Search for the first free slot
    for slot in range(1, TOTAL_SLOTS + 1):

        if slot not in occupied_slots:

            return slot


    return None


# ------------------------------------------------------------
# ADD VEHICLE
# ------------------------------------------------------------

def add_vehicle(registration, arrival_time, parking_slot):

    connection = get_connection()


    try:

        connection.execute("""
            INSERT INTO vehicles
            (registration, arrival_time, parking_slot)

            VALUES (?, ?, ?)
        """, (
            registration,
            arrival_time,
            parking_slot
        ))


        connection.commit()

        success = True


    except sqlite3.IntegrityError:

        # Vehicle already exists
        success = False


    connection.close()

    return success


# ------------------------------------------------------------
# FIND VEHICLE
# ------------------------------------------------------------

def find_vehicle(registration):

    connection = get_connection()


    vehicle = connection.execute(
        """
        SELECT *
        FROM vehicles
        WHERE registration = ?
        """,
        (registration,)
    ).fetchone()


    connection.close()

    return vehicle


# ------------------------------------------------------------
# REMOVE VEHICLE
# ------------------------------------------------------------

def remove_vehicle(registration):

    connection = get_connection()


    connection.execute(
        """
        DELETE FROM vehicles
        WHERE registration = ?
        """,
        (registration,)
    )


    connection.commit()

    connection.close()
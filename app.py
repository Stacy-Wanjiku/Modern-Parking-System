# ============================================================
#              MODERN PARKING SYSTEM
#              Main Application File
# ============================================================

from flask import Flask, render_template, request, redirect, url_for

from datetime import datetime

# Import functions from our database file
from database import (
    initialize_database,
    get_available_slots,
    get_next_available_slot,
    add_vehicle,
    find_vehicle,
    remove_vehicle
)


# ------------------------------------------------------------
# CREATE FLASK APPLICATION
# ------------------------------------------------------------

app = Flask(__name__)


# Total number of parking slots
TOTAL_SLOTS = 50


# ------------------------------------------------------------
# CALCULATE PARKING FEE
# ------------------------------------------------------------

def calculate_fee(hours):
    """
    Calculates the parking fee according to the
    parking charges in the assignment.
    """

    if hours <= 0.5:
        return 0

    elif hours <= 2:
        return 50

    elif hours <= 4:
        return 100

    elif hours <= 6:
        return 300

    else:
        return 500


# ------------------------------------------------------------
# HOME / DASHBOARD
# ------------------------------------------------------------

@app.route("/")
def home():

    # Get the number of available parking slots
    available = get_available_slots()

    # Calculate occupied slots
    occupied = TOTAL_SLOTS - available

    return render_template(
        "index.html",
        total=TOTAL_SLOTS,
        available=available,
        occupied=occupied
    )


# ------------------------------------------------------------
# VEHICLE ENTRY
# ------------------------------------------------------------

@app.route("/entry", methods=["GET", "POST"])
def entry():

    if request.method == "POST":

        # Get vehicle registration number
        registration = request.form["registration"].strip().upper()

        # Check if parking is full
        if get_available_slots() <= 0:

            return render_template(
                "entry.html",
                message="Parking is full. No available slots."
            )


        # Find an available parking slot
        parking_slot = get_next_available_slot()

        # Record the current time
        arrival_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # Add the vehicle to the database
        success = add_vehicle(
            registration,
            arrival_time,
            parking_slot
        )


        # Check whether the vehicle was successfully added
        if success:

            return render_template(
                "entry.html",
                success=True,
                registration=registration,
                parking_slot=parking_slot,
                arrival_time=arrival_time
            )

        else:

            return render_template(
                "entry.html",
                message="This vehicle is already inside the parking area."
            )


    return render_template("entry.html")


# ------------------------------------------------------------
# VEHICLE EXIT
# ------------------------------------------------------------

@app.route("/exit", methods=["GET", "POST"])
def exit():

    if request.method == "POST":

        # Get vehicle registration number
        registration = request.form["registration"].strip().upper()


        # Search for the vehicle
        vehicle = find_vehicle(registration)


        # Check if vehicle exists
        if vehicle is None:

            return render_template(
                "exit.html",
                message="Vehicle not found. Please check the registration number."
            )


        # Get the recorded arrival time
        arrival_time = datetime.strptime(
            vehicle["arrival_time"],
            "%Y-%m-%d %H:%M:%S"
        )


        # Record the current exit time
        exit_time = datetime.now()


        # Calculate how long the vehicle stayed
        duration = exit_time - arrival_time


        # Convert duration into hours
        hours = duration.total_seconds() / 3600


        # Calculate parking fee
        fee = calculate_fee(hours)


        # Get payment entered by the driver
        payment = float(request.form["payment"])


        # Check if payment is enough
        if payment < fee:

            return render_template(
                "exit.html",
                message=f"Insufficient payment. Required amount is KSh {fee}."
            )


        # Calculate change
        change = payment - fee


        # Remove vehicle from active parking records
        remove_vehicle(registration)


        # Get updated number of available slots
        available = get_available_slots()


        # Simulate opening the exit barrier
        barrier_status = "OPEN"


        return render_template(
            "exit.html",
            success=True,
            registration=registration,
            parking_slot=vehicle["parking_slot"],
            arrival_time=arrival_time,
            exit_time=exit_time,
            hours=hours,
            fee=fee,
            payment=payment,
            change=change,
            available=available,
            barrier=barrier_status
        )


    return render_template("exit.html")



if __name__ == "__main__":

    # Create the database when the program starts
    initialize_database()

    # Start the Flask web server
    app.run(debug=True)
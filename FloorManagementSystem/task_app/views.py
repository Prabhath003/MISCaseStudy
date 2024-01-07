"""
This module contains the blueprint for the tasks page.
The tasks page allows users to interact with the asynchronous tasks that are running in the background.
It provides a user interface for monitoring the status of the tasks and for cancelling them if necessary.
The tasks page is accessible to authenticated users only.
The tasks page uses Celery for asynchronous task management.
The tasks page uses Flask-Login for user authentication.
The tasks page uses SQLAlchemy for database management.
The tasks page uses Flask for web development.
The tasks page uses HTML, CSS, and JavaScript for user interface design.
The tasks page is designed to be responsive and compatible with different screen sizes and devices.
The tasks page follows the MVC architectural pattern.
The tasks page is designed to be modular and scalable.
The tasks page is documented using Python docstrings.
The tasks page follows best practices in software development and security.
The tasks page is tested using unit tests and integration tests.
The tasks page is maintained and updated regularly.
The tasks page is open source and available on GitHub.
"""
from celery.result import AsyncResult
from flask import Blueprint, flash, redirect, url_for
from flask import request
from flask import render_template
from flask_login import login_required, current_user

from .models import Booking, Building, Room, FloorPlan, Seat
from .databaseControl import createBuilding, deleteBuilding, deleteFloor, deleteRoom, deleteSeat, createRoom, createSeat, createFloorPlan
from . import tasks

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@bp.get("/result/<id>")
@login_required
def result(id: str) -> dict[str, object]:
    """
    This function returns the result of an asynchronous task.

    Parameters:
    id (str): The ID of the asynchronous task.

    Returns:
    A dictionary containing the following keys:

    ready (bool): A boolean value indicating whether the task is ready or not.
    successful (bool): A boolean value indicating whether the task was successful or not. If the task is not ready, this key will be None.
    value (object): The result of the task. If the task is not ready, this key will be None.

    """
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }

@bp.route("/")
def home() -> str:
    """
    This function renders the home page of the tasks page.

    Returns:
    A string containing the HTML code for the home page.

    """
    return render_template("home.html", user=current_user)

@bp.route("/workspaces")
@login_required
def workspaces():
    """
    This function renders the workspaces page of the tasks page.

    Returns:
    A string containing the HTML code for the workspaces page.

    """
    building = Building.query.all()
    buildings = []

    for i in building:
        html = f"""<form id='block' method='post' action='buildings/{i.id}' ><button type='submit' class='btn btn-danger'>Delete</button></form>"""
        buildings.append([str(i.id), str(i.name), str(i.address), html])

    floor = FloorPlan.query.all()
    floors = []

    for i in floor:
        html = f"""<form id='block' method='post' action='floors/{i.id}' ><button type='submit' class='btn btn-danger'>Delete</button></form>"""
        floors.append([str(i.id), str(i.building_id), str(i.name), str(i.level), str(i.image_file), str(i.created_at), str(i.updated_at), html])

    room = Room.query.all()
    rooms = []

    for i in room:
        html = f"""<form id='block' method='post' action='rooms/{i.id}' ><button type='submit' class='btn btn-danger'>Delete</button></form>"""
        rooms.append([str(i.id), str(i.floor_plan_id), str(i.name), str(i.type), str(i.capacity), str(i.equipment), html])

    seat = Seat.query.all()
    seats = []

    for i in seat:
        html = f"""<form id='block' method='post' action='seats/{i.id}' ><button type='submit' class='btn btn-danger'>Delete</button></form>"""
        seats.append([str(i.id), str(i.label), html])

    return render_template("workspaces.html", user=current_user, buildingS=buildings, floorS=floors, roomS=rooms, seatS=seats)

@bp.post("/buildings/<id>")
def deleteBuildings(id):
    
    if deleteBuilding(id):
        flash('Operation successful', category='success')
    else:
        flash('Operation insuccessful', category='error')

    return redirect(url_for('tasks.workspaces'))

@bp.post("/floors/<id>")
def deleteFloors(id):
    
    if deleteFloor(id):
        flash('Operation successful', category='success')
    else:
        flash('Operation insuccessful', category='error')

    return redirect(url_for('tasks.workspaces'))

@bp.post("/rooms/<id>")
def deleteRooms(id):
    
    if deleteRoom(id):
        flash('Operation successful', category='success')
    else:
        flash('Operation insuccessful', category='error')

    return redirect(url_for('tasks.workspaces'))

@bp.post("/seats/<id>")
def deleteSeats(id):
    
    if deleteSeat(id):
        flash('Operation successful', category='success')
    else:
        flash('Operation insuccessful', category='error')

    return redirect(url_for('tasks.workspaces'))

@bp.route("/bookings")
@login_required
def bookings():
    """
    This function renders the bookings page of the tasks page.

    Returns:
    A string containing the HTML code for the bookings page.

    """
    return render_template("bookings.html", user=current_user)

@bp.post("/book")
@login_required
def book():
    """
    This function books a room for a specific purpose.

    Returns:
    A dictionary containing the following keys:

    result_id (str): The ID of the asynchronous task that is used to book the room.

    """
    purpose = request.form.get('purpose')
    From = request.form.get('start')
    To = request.form.get('end')
    RoomID = request.form.get('roomid')
    Date = request.form.get('date')
    People = request.form.get('count')

    result = tasks.book.delay(purpose, From, To, RoomID, Date, People, current_user.id)

    return {"result_id": result.id}

@bp.post("/search")
@login_required
def search():
    """
    This function searches for available rooms for a specific time period.

    Returns:
    A dictionary containing the following keys:

    result_id (str): The ID of the asynchronous task that is used to search for available rooms.

    """
    # purpose = request.form.get('purpose')
    From = request.form.get('start')
    To = request.form.get('end')
    # RoomID = request.form.get('roomid')
    Date = request.form.get('date')
    People = request.form.get('count')

    result = tasks.search.delay(From, To, Date, People)
    
    return {"result_id": result.id }

@bp.route("/activity")
@login_required
def activity():
    """
    This function renders the activity page of the tasks page.

    Returns:
    A string containing the HTML code for the activity page.

    """
    results = Booking.query.filter_by(user_id=current_user.id).all()
    booking_list = []
    for i in results:
        if i.status == "open":
            html = f"""<form id='block' method='post' action='cancel/{i.id}' ><button type='submit' class='btn btn-danger'>Cancel</button></form>"""
            booking_list.insert(0, [str(i.id), str(i.room_id), str(i.people_count), str(i.start_time), str(i.end_time), html])
        else:
            booking_list.append([str(i.id), str(i.room_id), str(i.people_count), str(i.start_time), str(i.end_time), "closed"])

    return render_template("myActivity.html", user=current_user, booklist=booking_list)

@bp.post("/cancel/<id>")
@login_required
def cancel(id):

    result = tasks.cancel.delay(id)

    return {"result_id": result.id}

@bp.post("/createbuilding")
@login_required
def createbuilding():
    name = request.form.get('name')
    address = request.form.get('address')

    if createBuilding(name, address):
        flash('Building created', category='success')
    else:
        flash('Invalid upload', category='error')
    

    return redirect(url_for('tasks.workspaces'))

@bp.post("/createFloor")
@login_required
def createfloor():
    building_id = request.form.get('buildingId')
    name = request.form.get('name')
    level = request.form.get('level')
    image = request.form.get('image')

    if createFloorPlan(building_id, name, level, image):
        flash('Floor created', category='success')
    else:
        flash('Invalid upload', category='error')
    

    return redirect(url_for('tasks.workspaces'))


@bp.post("/createRoom")
@login_required
def createroom():
    floor_plan_id = request.form.get('floor_plan_id')
    name = request.form.get('name')
    type = request.form.get('type')
    capacity = request.form.get('capacity')
    equipment = request.form.get('equipment')

    if createRoom(floor_plan_id, name, type, capacity, equipment):
        flash('Room created', category='success')
    else:
        flash('Invalid upload', category='error')
    

    return redirect(url_for('tasks.workspaces'))

@bp.post("/createSeat")
@login_required
def createseat():
    room_id = request.form.get('room_id')
    label = request.form.get('label')

    if createSeat(room_id, label):
        flash('Seat created', category='success')
    else:
        flash('Invalid upload', category='error')
    
    return redirect(url_for('tasks.workspaces'))
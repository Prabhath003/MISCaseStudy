from celery import shared_task
from sqlalchemy import and_, or_
from datetime import datetime

from . import db
from .models import Booking, Room

"""
This function is used to cancel a booking based on the booking id.

Args:
    id (int): The id of the booking to be cancelled.

Returns:
    None: If the booking is found and cancelled, returns None. If the booking is not found, prints an error message.

"""
@shared_task()
def cancel(id):
    row = db.session.query(Booking).filter(Booking.id == id).first()
    if row:
        row.status = "closed"
        db.session.commit()
    else:
        print("Corresponding ID is not found!")

"""
This function is used to search for available rooms for a booking based on the specified criteria.

Args:
    From (str): The start time of the booking, in the format "HH:MM".
    To (str): The end time of the booking, in the format "HH:MM".
    date (str): The date of the booking, in the format "YYYY-MM-DD".
    People (int): The number of people in the booking.

Returns:
    list: A list of available rooms, where each room is represented as a list of its attributes. The attributes are in the following order: room id, capacity, floor plan id, room type, equipment, and a button to choose the room.

"""
@shared_task(ignore_result=False)
def search(From, To, date, People):

    date = list(map(int, date.split('-')))
    From = list(map(int, From.split(':')))
    To = list(map(int, To.split(':')))
    From = datetime(date[0], date[1], date[2], From[0], From[1])
    To = datetime(date[0], date[1], date[2], To[0], To[1])

    available_rooms = db.session.query(Room, Booking).outerjoin(Booking, Booking.room_id == Room.id).filter(
            and_(
            Room.capacity >= People,  # Filter for rooms with at least 5 seats
            # Check for closed bookings within the desired time frame
            or_(Room.id != Booking.room_id, Booking.status != 'open',
                and_(Booking.start_time >= To,
                    Booking.end_time <= From))
            )).all()

    rooms = []
    for i in available_rooms:
        html = f"""<button class="btn btn-primary" onclick="changeElementValue('roomid', {i[0].id})">Choose</button>"""
        rooms.append([i[0].id, str(i[0].capacity), str(i[0].floor_plan_id), str(i[0].type), str(i[0].equipment), html])

    return rooms

"""
This function is used to book a room based on the specified criteria. If a booking with the same criteria already exists, it will be updated with the new information.

Args:
    purpose (str): The purpose of the booking.
    From (str): The start time of the booking, in the format "HH:MM".
    To (str): The end time of the booking, in the format "HH:MM".
    RoomID (int): The id of the room to be booked.
    date (str): The date of the booking, in the format "YYYY-MM-DD".
    People (int): The number of people in the booking.
    id (int): The id of the user making the booking.

Returns:
    None: If the booking is successful, returns None. If there is an error, prints the error message.

"""
@shared_task(Bind=True, ignore_result=True)
def book(purpose, From, To, RoomID, date, People, id):

    date = list(map(int, date.split('-')))
    From = list(map(int, From.split(':')))
    To = list(map(int, To.split(':')))
    From = datetime(date[0], date[1], date[2], From[0], From[1])
    To = datetime(date[0], date[1], date[2], To[0], To[1])

    ## Repeition handling cases

    new_Booking = Booking(purpose=purpose, user_id=id, start_time=From, end_time=To, room_id=RoomID, people_count=People)
    try:
        db.session.add(new_Booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

        row = db.session.query(Booking).filter_by(and_(user_id=id, start_time=From, end_time=To, room_id=RoomID)).first()

        if row:
            row.status = "open"
            row.people_count = People
            db.session.commit()

    return



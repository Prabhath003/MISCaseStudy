"""
This module defines the database schema for a fictitious event space management system.

Classes:
    FloorPlan: A class that represents a floor plan in the event space.
    Room: A class that represents a room in the event space.
    Seat: A class that represents a seat in a room.
    Building: A class that represents a building in the event space.
    User: A class that represents a user in the system.
    Booking: A class that represents a booking in the system.

Relationships:
    FloorPlan.rooms: A relationship that connects FloorPlan to Room.
    Room.seats: A relationship that connects Room to Seat.
    Room.bookings: A relationship that connects Room to Booking.
    Seat.room: A relationship that connects Seat to Room.
    Booking.room: A relationship that connects Booking to Room.
    Booking.user: A relationship that connects Booking to User.

"""
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import timedelta, datetime
# from geoalchemy2 import Geometry


class FloorPlan(db.Model):
    """
    A class that represents a floor plan in the event space.

    Attributes:
        id: The primary key of the FloorPlan.
        building_id: The foreign key to the Building that the FloorPlan belongs to.
        name: The name of the FloorPlan.
        level: The level of the FloorPlan.
        image_file: The file name of the image of the FloorPlan.
        created_at: The datetime when the FloorPlan was created.
        updated_at: The datetime when the FloorPlan was last updated.
        rooms: A relationship that connects FloorPlan to Room.
    """
    __tablename__ = 'floor_plans'
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.id', ondelete='CASCADE'))
    name = Column(String)
    level = Column(Integer, default=0)
    image_file = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    rooms = relationship("Room", backref="floor_plan", cascade="all, delete-orphan")


class Room(db.Model):
    """
    A class that represents a room in the event space.

    Attributes:
        id: The primary key of the Room.
        floor_plan_id: The foreign key to the FloorPlan that the Room belongs to.
        name: The name of the Room.
        type: The type of the Room (e.g., lecture hall, workshop room).
        capacity: The capacity of the Room.
        equipment: The equipment available in the Room.
        seats: A relationship that connects Room to Seat.
        bookings: A relationship that connects Room to Booking.
    """
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    floor_plan_id = Column(Integer, ForeignKey('floor_plans.id', ondelete='CASCADE'))
    name = Column(String)
    type = Column(String)
    capacity = Column(Integer)
    equipment = Column(String)
    seats = relationship("Seat", backref="room", cascade="all, delete-orphan")
    bookings = relationship("Booking", backref="room")


class Seat(db.Model):
    """
    A class that represents a seat in a room.

    Attributes:
        id: The primary key of the Seat.
        room_id: The foreign key to the Room that the Seat belongs to.
        label: The label of the Seat.
    """
    __tablename__ = 'seats'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete='CASCADE'))
    label = Column(String)


class Building(db.Model):
    """
    A class that represents a building in the event space.

    Attributes:
        id: The primary key of the Building.
        name: The name of the Building.
        address: The address of the Building.
        floor_plans: A relationship that connects Building to FloorPlan.
    """
    __tablename__ = 'buildings'
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        db.UniqueConstraint('name', 'address'),
      )
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    address = Column(String, unique=True)
    floor_plans = relationship("FloorPlan", backref="building", cascade="all, delete-orphan")


class User(db.Model, UserMixin):
    """
    A class that represents a user in the system.

    Attributes:
        id: The primary key of the User.
        email: The email of the User.
        role: The role of the User (e.g., admin, regular user).
        password: The password of the User.
        first_name: The first name of the User.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    role = Column(String(150), nullable=False)
    password = Column(String(150), nullable=False)
    first_name = Column(String(150), nullable=False)


class Booking(db.Model):
    """
    A class that represents a booking in the system.

    Attributes:
        id: The primary key of the Booking.
        room_id: The foreign key to the Room that the Booking is for.
        user_id: The foreign key to the User that made the Booking.
        people_count: The number of people in the Booking.
        start_time: The start time of the Booking.
        end_time: The end time of the Booking.
        purpose: The purpose of the Booking.
    """
    __tablename__ = 'bookings'
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        db.UniqueConstraint('room_id', 'user_id', 'start_time', 'end_time'),
      )
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    people_count = Column(Integer, default=1)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), default=datetime.now()+timedelta(hours=1))
    purpose = Column(String, default="")
    status = Column(String, default="open")
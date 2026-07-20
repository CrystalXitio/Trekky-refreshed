from flask_login import UserMixin
from datetime import datetime
import random
from app import db

class User(db.Model, UserMixin):
	__tablename__='user'

	user_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_display_id=db.Column(db.String(4), unique=True, nullable=False)
	user_full_name=db.Column(db.String(150), nullable=True)
	user_dob=db.Column(db.Date, nullable=True)
	user_contact_no=db.Column(db.String(20), nullable=True)
	user_email=db.Column(db.String(255), unique=True, nullable=False)
	user_password_hash=db.Column(db.String(255), nullable=False)
	user_role=db.Column(db.String(10), db.CheckConstraint("user_role IN ('admin', 'staff', 'trekker')"), nullable=False)

	staff_profile=db.relationship('Staff', back_populates='user', uselist=False)
	bookings=db.relationship('Booking', back_populates='user')
	reviews=db.relationship('Review', back_populates='user')

	def get_id(self):
		return str(self.user_id)

	@staticmethod
	def generate_display_id(role):
		prefix = ''
		if role == 'admin': prefix = 'A'
		elif role == 'staff': prefix = 'S'
		elif role == 'trekker': prefix = 'U'
		else: prefix = 'U'
		
		while True:
			new_id = f"{prefix}{str(random.randint(1, 999)).zfill(3)}"
			existing = User.query.filter_by(user_display_id=new_id).first()
			if not existing:
				return new_id

class Staff(db.Model):
	__tablename__='staff'

	staff_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True, nullable=False)
	staff_name=db.Column(db.String(150), nullable=False)
	staff_contact_details=db.Column(db.String(255), nullable=False)
	staff_status=db.Column(db.String(15), db.CheckConstraint("staff_status IN ('Pending', 'Approved', 'Blacklisted')"), nullable=False, default='Pending')

	user=db.relationship('User', back_populates='staff_profile')
	treks=db.relationship('Trek', back_populates='assigned_staff')

class Trek(db.Model):
	__tablename__='trek'

	trek_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	trek_display_id=db.Column(db.String(4), unique=True, nullable=False)
	trek_name=db.Column(db.String(200), nullable=False)
	trek_location=db.Column(db.String(200), nullable=False)
	trek_difficulty=db.Column(db.String(10), db.CheckConstraint("trek_difficulty IN ('Easy', 'Moderate', 'Hard')"), nullable=False)
	trek_duration=db.Column(db.Integer, nullable=False)
	trek_available_slots=db.Column(db.Integer, nullable=False)
	trek_status=db.Column(db.String(15), db.CheckConstraint("trek_status IN ('Draft', 'Upcoming', 'Booking Open', 'Closed', 'Ongoing', 'Completed', 'Cancelled')"), nullable=False, default='Draft')
	trek_start_date=db.Column(db.Date, nullable=False)
	trek_end_date=db.Column(db.Date, nullable=False)
	trek_image_filename=db.Column(db.String(255), nullable=True)
	assigned_staff_id=db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)

	assigned_staff=db.relationship('Staff', back_populates='treks')
	bookings=db.relationship('Booking', back_populates='trek')
	reviews=db.relationship('Review', back_populates='trek')

	@staticmethod
	def generate_display_id():
		while True:
			new_id = f"T{str(random.randint(1, 999)).zfill(3)}"
			existing = Trek.query.filter_by(trek_display_id=new_id).first()
			if not existing:
				return new_id

class Booking(db.Model):
	__tablename__='booking'

	booking_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	booking_display_id=db.Column(db.String(4), unique=True, nullable=False)
	user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	trek_id=db.Column(db.Integer, db.ForeignKey('trek.trek_id'), nullable=False)
	booking_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
	booking_status=db.Column(db.String(15), db.CheckConstraint("booking_status IN ('Booked', 'Cancelled', 'Refunded', 'Trek Abandoned', 'Completed')"), nullable=False, default='Booked')

	user=db.relationship('User', back_populates='bookings')
	trek=db.relationship('Trek', back_populates='bookings')

	@staticmethod
	def generate_display_id():
		while True:
			new_id = f"B{str(random.randint(1, 999)).zfill(3)}"
			existing = Booking.query.filter_by(booking_display_id=new_id).first()
			if not existing:
				return new_id

class Review(db.Model):
	__tablename__='review'

	review_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	review_display_id=db.Column(db.String(4), unique=True, nullable=True)
	user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	trek_id=db.Column(db.Integer, db.ForeignKey('trek.trek_id'), nullable=False)
	rating=db.Column(db.Integer, db.CheckConstraint("rating >= 1 AND rating <= 5"), nullable=False)
	review_text=db.Column(db.Text, nullable=False)
	created_at=db.Column(db.DateTime, nullable=False, default=datetime.now)

	user=db.relationship('User', back_populates='reviews')
	trek=db.relationship('Trek', back_populates='reviews')

	@staticmethod
	def generate_display_id():
		while True:
			new_id = f"R{str(random.randint(1, 999)).zfill(3)}"
			existing = Review.query.filter_by(review_display_id=new_id).first()
			if not existing:
				return new_id

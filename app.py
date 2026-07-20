import sys
if __name__ == '__main__':
	sys.modules['app'] = sys.modules[__name__]

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

db=SQLAlchemy()
login_manager=LoginManager()

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

app=Flask(__name__)

app.config['SECRET_KEY']='trekky-super-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)
login_manager.init_app(app)

from models import User, Staff, Trek, Booking

with app.app_context():
	db.create_all()

	# Safe migration: add trek_image_filename column if it doesn't exist yet
	try:
		db.session.execute(db.text('ALTER TABLE trek ADD COLUMN trek_image_filename VARCHAR(255)'))
		db.session.commit()
	except Exception:
		db.session.rollback()  # Column already exists — ignore

	# Seed image filenames for starter treks
	image_map = {
		'T001': 'treks/ebc.png',
		'T002': 'treks/mont-blanc.png',
		'T003': 'treks/zion.png',
	}
	for display_id, filename in image_map.items():
		trek = Trek.query.filter_by(trek_display_id=display_id).first()
		if trek and not trek.trek_image_filename:
			trek.trek_image_filename = filename
	try:
		db.session.commit()
	except Exception:
		db.session.rollback()

	# Initialize Core System Accounts (Admin, Approved Staff, Trekker) if missing
	admin_user = User.query.filter_by(user_role='admin').first()
	if admin_user is None:
		admin_user = User(
			user_display_id='A001',
			user_email='admin@trekky.com',
			user_password_hash=generate_password_hash('Admin@1234'),
			user_role='admin',
			user_full_name='System Administrator',
			user_dob=date(1980, 1, 1),
			user_contact_no='000-000-0000'
		)
		db.session.add(admin_user)
		db.session.commit()

	staff_user = User.query.filter_by(user_email='staff@trekky.com').first()
	if not staff_user:
		staff_user = User(
			user_display_id='S001',
			user_email='staff@trekky.com',
			user_password_hash=generate_password_hash('password123'),
			user_role='staff',
			user_full_name='Staff User',
			user_dob=date(1985, 5, 20),
			user_contact_no='+91 9876543210'
		)
		db.session.add(staff_user)
		db.session.commit()

	staff_profile = Staff.query.filter_by(user_id=staff_user.user_id).first()
	if not staff_profile:
		staff_profile = Staff(
			user_id=staff_user.user_id,
			staff_name=staff_user.user_full_name,
			staff_contact_details=staff_user.user_contact_no,
			staff_status='Approved'
		)
		db.session.add(staff_profile)
		db.session.commit()

	trekker_user = User.query.filter_by(user_email='trekker@trekky.com').first()
	if not trekker_user:
		trekker_user = User(
			user_display_id='U001',
			user_email='trekker@trekky.com',
			user_password_hash=generate_password_hash('password123'),
			user_role='trekker',
			user_full_name='Trekker User',
			user_dob=date(1995, 8, 15),
			user_contact_no='+91 9876543211'
		)
		db.session.add(trekker_user)
		db.session.commit()

from routes import *

if __name__ == '__main__':
	app.debug = True 
	
	from livereload import Server
	server = Server(app.wsgi_app)
	
	server.watch('templates/')
	server.watch('static/css/')
	
	server.serve(port=5000)

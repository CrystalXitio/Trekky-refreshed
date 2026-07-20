from flask import render_template, redirect, url_for, request, flash, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io
import base64
from app import app, db
from models import User, Staff, Trek, Booking, Review
from datetime import datetime

def admin_required():
	if not current_user.is_authenticated or current_user.user_role != 'admin':
		abort(403)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/toggle_theme')
def toggle_theme():
	if session.get('theme') == 'dark':
		session['theme'] = 'light'
	else:
		session['theme'] = 'dark'
	return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		
		try:
			user = User.query.filter_by(user_email=email).first()
			if user and check_password_hash(user.user_password_hash, password):
				login_user(user)
				flash('Authentication successful.', 'success')
				return redirect(url_for('dashboard'))
			else:
				flash('Invalid credentials.', 'danger')
		except Exception as e:
			flash('A database error occurred during login.', 'danger')
			
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
		
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		role = request.form.get('role')
		contact = request.form.get('contact')
		
		if not email or not password or not role:
			flash('Incomplete parameters provided.', 'warning')
			return redirect(url_for('register'))
			
		try:
			existing_user = User.query.filter_by(user_email=email).first()
			if existing_user:
				flash('User email already exists.', 'danger')
				return redirect(url_for('register'))
				
			if contact:
				existing_contact = User.query.filter_by(user_contact_no=contact).first()
				if existing_contact:
					flash('Contact number already exists.', 'danger')
					return redirect(url_for('register'))
				
			hashed_password = generate_password_hash(password)
			display_id = User.generate_display_id(role)
			new_user = User(user_display_id=display_id, user_email=email, user_contact_no=contact, user_password_hash=hashed_password, user_role=role)
			
			db.session.add(new_user)
			db.session.commit()
			
			if role == 'staff':
				staff_name = request.form.get('staff_name')
				new_staff = Staff(user_id=new_user.user_id,
					staff_name=staff_name or 'Pending Name',
					staff_contact_details=contact or 'N/A',
					staff_status='Pending')
				db.session.add(new_staff)
				db.session.commit()
				
			flash('Registration successful. You may now authenticate.', 'success')
			return redirect(url_for('login'))
		except Exception as e:
			db.session.rollback()
			flash('A system error occurred during registration. Please try again.', 'danger')
			return redirect(url_for('register'))
			
	return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Session terminated.', 'info')
	return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
	if current_user.user_role == 'admin':
		return redirect(url_for('admin_dashboard'))
	elif current_user.user_role == 'staff':
		if not current_user.staff_profile:
			flash("Staff profile missing.", "danger")
			return redirect(url_for('index'))
			
		staff = current_user.staff_profile
		assigned_treks = []
		if staff.staff_status == 'Approved':
			assigned_treks = Trek.query.filter_by(assigned_staff_id=staff.staff_id).all()
		
		limit_treks = int(request.args.get('limit_treks', 6))
		return render_template('staff_dashboard.html', staff=staff, treks=assigned_treks, limit_treks=limit_treks)
	elif current_user.user_role == 'trekker':
		import random
		open_treks = Trek.query.filter(Trek.trek_status == 'Booking Open', Trek.trek_available_slots > 0).all()
		recommended_treks = random.sample(open_treks, min(3, len(open_treks)))
		
		location = request.args.get('location', '')
		difficulties = request.args.getlist('difficulty')
		statuses = request.args.getlist('status')
		limit_treks = int(request.args.get('limit_treks', 6))
		limit_bookings = int(request.args.get('limit_bookings', 6))
		start_date_str = request.args.get('start_date', '')
		end_date_str = request.args.get('end_date', '')
		
		query = Trek.query
		if statuses:
			query = query.filter(Trek.trek_status.in_(statuses))
		else:
			query = query.filter(Trek.trek_status.in_(['Upcoming', 'Booking Open', 'Closed', 'Ongoing', 'Completed']))
			
		if location:
			query = query.filter(Trek.trek_location.ilike(f"%{location}%"))
			
		if difficulties:
			query = query.filter(Trek.trek_difficulty.in_(difficulties))
			
		if start_date_str:
			try:
				start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
				query = query.filter(Trek.trek_start_date >= start_date)
			except ValueError:
				pass
				
		if end_date_str:
			try:
				end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
				query = query.filter(Trek.trek_end_date <= end_date)
			except ValueError:
				pass
				
		ledger_treks = query.all()
		booking_history = sorted(current_user.bookings, key=lambda x: x.booking_date, reverse=True)
		return render_template('trekker_dashboard.html', 
							   recommended_treks=recommended_treks, 
							   ledger_treks=ledger_treks, 
							   bookings=booking_history,
							   limit_treks=limit_treks,
							   limit_bookings=limit_bookings,
							   location=location, difficulties=difficulties, statuses=statuses,
							   start_date=start_date_str, end_date=end_date_str)
	else:
		abort(403)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
	admin_required()
	
	total_treks = Trek.query.count()
	trek_stats = {
		'draft': Trek.query.filter_by(trek_status='Draft').count(),
		'upcoming': Trek.query.filter_by(trek_status='Upcoming').count(),
		'open': Trek.query.filter_by(trek_status='Booking Open').count(),
		'closed': Trek.query.filter_by(trek_status='Closed').count(),
		'ongoing': Trek.query.filter_by(trek_status='Ongoing').count(),
		'completed': Trek.query.filter_by(trek_status='Completed').count(),
		'cancelled': Trek.query.filter_by(trek_status='Cancelled').count(),
	}

	total_users = User.query.count()
	total_admins = User.query.filter_by(user_role='admin').count()
	total_staff = User.query.filter_by(user_role='staff').count()
	total_trekkers = User.query.filter_by(user_role='trekker').count()

	total_bookings = Booking.query.count()
	booking_stats = {
		'booked': Booking.query.filter_by(booking_status='Booked').count(),
		'cancelled': Booking.query.filter_by(booking_status='Cancelled').count(),
		'refunded': Booking.query.filter_by(booking_status='Refunded').count(),
		'abandoned': Booking.query.filter_by(booking_status='Trek Abandoned').count(),
		'completed': Booking.query.filter_by(booking_status='Completed').count(),
	}
	
	u_role = request.args.getlist('u_role')
	u_name = request.args.get('u_name', '')
	t_location = request.args.get('t_location', '')
	t_difficulty = request.args.getlist('t_difficulty')
	t_status = request.args.getlist('t_status')
	t_start = request.args.get('t_start', '')
	t_end = request.args.get('t_end', '')
	b_trekker = request.args.get('b_trekker', '')
	b_trek = request.args.get('b_trek', '')
	b_staff = request.args.get('b_staff', '')
	b_status = request.args.getlist('b_status')
	
	users_query = User.query
	if u_name: users_query = users_query.filter((User.user_full_name.ilike(f"%{u_name}%")) | (User.user_email.ilike(f"%{u_name}%")))
	if u_role: users_query = users_query.filter(User.user_role.in_(u_role))
	
	treks_query = Trek.query
	if t_location: treks_query = treks_query.filter(Trek.trek_location.ilike(f"%{t_location}%"))
	if t_difficulty: treks_query = treks_query.filter(Trek.trek_difficulty.in_(t_difficulty))
	if t_status: treks_query = treks_query.filter(Trek.trek_status.in_(t_status))
	if t_start:
		try:
			s_date = datetime.strptime(t_start, '%Y-%m-%d').date()
			treks_query = treks_query.filter(Trek.trek_start_date >= s_date)
		except ValueError: pass
	if t_end:
		try:
			e_date = datetime.strptime(t_end, '%Y-%m-%d').date()
			treks_query = treks_query.filter(Trek.trek_end_date <= e_date)
		except ValueError: pass
		
	bookings_query = Booking.query.join(User).join(Trek).outerjoin(Staff, Trek.assigned_staff_id == Staff.staff_id)
	if b_trekker: bookings_query = bookings_query.filter((User.user_full_name.ilike(f"%{b_trekker}%")) | (User.user_email.ilike(f"%{b_trekker}%")))
	if b_trek: bookings_query = bookings_query.filter(Trek.trek_name.ilike(f"%{b_trek}%"))
	if b_staff: bookings_query = bookings_query.filter(Staff.staff_name.ilike(f"%{b_staff}%"))
	if b_status: bookings_query = bookings_query.filter(Booking.booking_status.in_(b_status))
	
	usort = request.args.get('usort')
	udir = request.args.get('udir', 'asc')
	if usort == 'id': users_query = users_query.order_by(User.user_display_id.asc() if udir == 'asc' else User.user_display_id.desc())
	elif usort == 'name': users_query = users_query.order_by(User.user_full_name.asc() if udir == 'asc' else User.user_full_name.desc())
	elif usort == 'email': users_query = users_query.order_by(User.user_email.asc() if udir == 'asc' else User.user_email.desc())
	elif usort == 'contact': users_query = users_query.order_by(User.user_contact_no.asc() if udir == 'asc' else User.user_contact_no.desc())
	elif usort == 'role': users_query = users_query.order_by(User.user_role.asc() if udir == 'asc' else User.user_role.desc())
	
	tsort = request.args.get('tsort')
	tdir = request.args.get('tdir', 'asc')
	if tsort == 'id': treks_query = treks_query.order_by(Trek.trek_id.asc() if tdir == 'asc' else Trek.trek_id.desc())
	elif tsort == 'name': treks_query = treks_query.order_by(Trek.trek_name.asc() if tdir == 'asc' else Trek.trek_name.desc())
	elif tsort == 'location': treks_query = treks_query.order_by(Trek.trek_location.asc() if tdir == 'asc' else Trek.trek_location.desc())
	elif tsort == 'difficulty': treks_query = treks_query.order_by(Trek.trek_difficulty.asc() if tdir == 'asc' else Trek.trek_difficulty.desc())
	elif tsort == 'slots': treks_query = treks_query.order_by(Trek.trek_available_slots.asc() if tdir == 'asc' else Trek.trek_available_slots.desc())
	elif tsort == 'status': treks_query = treks_query.order_by(Trek.trek_status.asc() if tdir == 'asc' else Trek.trek_status.desc())
	
	users_list = users_query.all()
	treks_list = treks_query.all()
	bookings_list = bookings_query.all()
	
	chart_data = None
	try:
		trek_ids = []
		booking_counts = []
		
		# Get the last 15 completed treks
		completed_treks = Trek.query.filter_by(trek_status='Completed').order_by(Trek.trek_end_date.desc()).limit(15).all()
		completed_treks.reverse() # Show oldest to newest left to right
		
		for trek in completed_treks:
			valid_bookings = len([b for b in trek.bookings if b.booking_status in ('Booked', 'Completed')])
			trek_ids.append(trek.trek_display_id)
			booking_counts.append(valid_bookings)
				
		if booking_counts:
			fig = plt.figure(figsize=(8, 4))
			ax = fig.add_subplot(111)
			
			if session.get('theme') == 'dark':
				bg_color = '#2d302d'
				text_color = '#e2e4e0'
				border_color = '#7a857a'
				bar_color = '#8dae8d'
			else:
				bg_color = '#ffffff'
				text_color = '#2c2a25'
				border_color = '#e5e0d8'
				bar_color = '#4a7c59'
			
			fig.patch.set_facecolor(bg_color)
			ax.set_facecolor(bg_color)
			
			plt.bar(trek_ids, booking_counts, color=bar_color)
			plt.title('Trekking Popularity (Last 15 Completed)', color=text_color)
			plt.ylabel('Total Bookings', color=text_color)
			plt.xlabel('Trek ID', color=text_color)
			plt.xticks(rotation=45, color=text_color)
			plt.yticks(range(0, max(booking_counts) + 2), color=text_color)
			
			for spine in ax.spines.values():
				spine.set_edgecolor(border_color)
				
			plt.tight_layout()
			
			img = io.BytesIO()
			plt.savefig(img, format='png')
			img.seek(0)
			chart_data = base64.b64encode(img.getvalue()).decode()
			plt.close()
	except Exception as e:
		pass
	
	limit_users = int(request.args.get('limit_users', 6))
	limit_treks = int(request.args.get('limit_treks', 6))
	limit_bookings = int(request.args.get('limit_bookings', 6))
	
	all_treks_master = Trek.query.all()

	return render_template('admin_dashboard.html', 
						   total_treks=total_treks, trek_stats=trek_stats,
						   total_users=total_users, total_admins=total_admins, total_staff=total_staff, total_trekkers=total_trekkers,
						   total_bookings=total_bookings, booking_stats=booking_stats,
						   users=users_list, treks=treks_list, bookings=bookings_list, all_treks=all_treks_master, chart_data=chart_data,
						   usort=usort, udir=udir, tsort=tsort, tdir=tdir,
						   u_name=u_name, u_role=u_role, t_location=t_location, t_difficulty=t_difficulty, t_status=t_status,
						   t_start=t_start, t_end=t_end, b_trekker=b_trekker, b_trek=b_trek, b_staff=b_staff, b_status=b_status,
						   limit_users=limit_users, limit_treks=limit_treks, limit_bookings=limit_bookings)
@app.route('/admin/staff/approve/<int:staff_id>', methods=['POST'])
@login_required
def admin_approve_staff(staff_id):
	admin_required()
	try:
		staff = Staff.query.get_or_404(staff_id)
		staff.staff_status = 'Approved'
		db.session.commit()
		flash(f'Staff {staff.staff_name} approved.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Error updating staff status.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/admin/staff/blacklist/<int:staff_id>', methods=['POST'])
@login_required
def admin_blacklist_staff(staff_id):
	admin_required()
	try:
		staff = Staff.query.get_or_404(staff_id)
		staff.staff_status = 'Blacklisted'
		db.session.commit()
		flash(f'Staff {staff.staff_name} blacklisted.', 'warning')
	except Exception as e:
		db.session.rollback()
		flash('Error updating staff status.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/blacklist/<int:user_id>', methods=['POST'])
@login_required
def admin_blacklist_user(user_id):
	admin_required()
	try:
		user = User.query.get_or_404(user_id)
		if user.user_role == 'admin':
			flash('Cannot deactivate an administrator.', 'danger')
			return redirect(url_for('admin_dashboard'))
			
		user.user_password_hash = "BANNED"
		db.session.commit()
		flash(f'User {user.user_email} deactivated securely.', 'warning')
	except Exception as e:
		db.session.rollback()
		flash('Error deactivating user.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/activate/<int:user_id>', methods=['POST'])
@login_required
def admin_activate_user(user_id):
	admin_required()
	try:
		user = User.query.get_or_404(user_id)
		user.user_password_hash = generate_password_hash('password123')
		db.session.commit()
		flash(f'User {user.user_email} activated. Temp pass: password123.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Error activating user.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
	admin_required()
	try:
		user = User.query.get_or_404(user_id)
		db.session.delete(user)
		db.session.commit()
		flash(f'User {user.user_email} permanently deleted.', 'warning')
	except Exception as e:
		db.session.rollback()
		flash('Cannot delete user (Foreign key constraints may exist).', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/create', methods=['GET', 'POST'])
@login_required
def admin_create_user():
	admin_required()
	if request.method == 'POST':
		email = request.form.get('email')
		role = request.form.get('role')
		password = request.form.get('password')
		contact = request.form.get('contact')
		full_name = request.form.get('full_name')
		dob_str = request.form.get('dob')
		
		try:
			existing = User.query.filter_by(user_email=email).first()
			if existing:
				flash('Email already exists.', 'danger')
				return redirect(url_for('admin_create_user'))
				
			if contact:
				existing_contact = User.query.filter_by(user_contact_no=contact).first()
				if existing_contact:
					flash('Contact number already exists.', 'danger')
					return redirect(url_for('admin_create_user'))
				
			hashed_password = generate_password_hash(password)
			display_id = User.generate_display_id(role)
			dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
			
			new_user = User(user_display_id=display_id, user_email=email, user_contact_no=contact, user_full_name=full_name, user_dob=dob, user_password_hash=hashed_password, user_role=role)
			db.session.add(new_user)
			db.session.commit()
			
			if role == 'staff':
				new_staff = Staff(user_id=new_user.user_id, staff_name=full_name or 'Pending Name', staff_contact_details=contact or 'N/A', staff_status='Pending')
				db.session.add(new_staff)
				db.session.commit()
				
			flash('User created successfully.', 'success')
			return redirect(url_for('admin_dashboard'))
		except Exception as e:
			db.session.rollback()
			flash('Error creating user.', 'danger')
			
	return render_template('admin_user_form.html', action='Create', user=None)

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
	admin_required()
	user = User.query.get_or_404(user_id)
	if request.method == 'POST':
		try:
			user.user_email = request.form.get('user_email')
			role = request.form.get('user_role')
			
			if user.user_role != role:
				user.user_role = role
				if role == 'staff':
					existing_staff = Staff.query.filter_by(user_id=user.user_id).first()
					if not existing_staff:
						new_staff = Staff(user_id=user.user_id, staff_name='Pending Name', staff_contact_details='N/A', staff_status='Pending')
						db.session.add(new_staff)
				else:
					existing_staff = Staff.query.filter_by(user_id=user.user_id).first()
					if existing_staff:
						db.session.delete(existing_staff)
			
			password = request.form.get('user_password')
			if password:
				user.user_password_hash = generate_password_hash(password)
				
			db.session.commit()
			flash('User updated successfully.', 'success')
			return redirect(url_for('admin_dashboard'))
		except Exception as e:
			db.session.rollback()
			flash('Error updating user.', 'danger')
			
	return render_template('admin_user_form.html', action='Edit', user=user)

@app.route('/admin/trek/create', methods=['GET', 'POST'])
@login_required
def admin_create_trek():
	admin_required()
	if request.method == 'POST':
		name = request.form.get('trek_name')
		location = request.form.get('trek_location')
		difficulty = request.form.get('trek_difficulty')
		slots = request.form.get('trek_available_slots')
		status = request.form.get('trek_status')
		start_date_str = request.form.get('trek_start_date')
		end_date_str = request.form.get('trek_end_date')
		staff_id = request.form.get('assigned_staff_id')
		
		try:
			slots = int(slots)
			start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
			end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
			duration = (end_date - start_date).days + 1
			
			if slots < 0:
				flash('Available slots cannot be negative.', 'danger')
				return redirect(url_for('admin_create_trek'))
				
			if start_date >= end_date:
				flash('Start date must be strictly before end date.', 'danger')
				return redirect(url_for('admin_create_trek'))
				
			display_id = Trek.generate_display_id()
			new_trek = Trek(trek_display_id=display_id,
				trek_name=name,
				trek_location=location,
				trek_difficulty=difficulty,
				trek_duration=duration,
				trek_available_slots=slots,
				trek_status=status,
				trek_start_date=start_date,
				trek_end_date=end_date,
				assigned_staff_id=int(staff_id) if staff_id else None)
			db.session.add(new_trek)
			db.session.commit()
			flash('Trek created successfully.', 'success')
			return redirect(url_for('admin_dashboard'))
		except ValueError:
			flash('Invalid input formatting.', 'danger')
		except Exception as e:
			db.session.rollback()
			flash('Database constraint error.', 'danger')
			
	staff_members = Staff.query.filter_by(staff_status='Approved').all()
	return render_template('admin_trek_form.html', staff_members=staff_members, action='Create', trek=None)

@app.route('/admin/trek/edit/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_trek(trek_id):
	admin_required()
	trek = Trek.query.get_or_404(trek_id)
	if request.method == 'POST':
		try:
			trek.trek_name = request.form.get('trek_name')
			trek.trek_location = request.form.get('trek_location')
			trek.trek_difficulty = request.form.get('trek_difficulty')
			slots = int(request.form.get('trek_available_slots'))
			trek.trek_status = request.form.get('trek_status')
			
			start_date = datetime.strptime(request.form.get('trek_start_date'), '%Y-%m-%d').date()
			end_date = datetime.strptime(request.form.get('trek_end_date'), '%Y-%m-%d').date()
			trek.trek_duration = (end_date - start_date).days + 1
			
			staff_id = request.form.get('assigned_staff_id')
			trek.assigned_staff_id = int(staff_id) if staff_id else None
			
			if slots < 0:
				flash('Available slots cannot be negative.', 'danger')
				return redirect(url_for('admin_edit_trek', trek_id=trek.trek_id))
				
			if start_date >= end_date:
				flash('Start date must be strictly before end date.', 'danger')
				return redirect(url_for('admin_edit_trek', trek_id=trek.trek_id))
				
			trek.trek_available_slots = slots
			trek.trek_start_date = start_date
			trek.trek_end_date = end_date
			
			db.session.commit()
			flash('Trek updated successfully.', 'success')
			return redirect(url_for('admin_dashboard'))
		except Exception as e:
			db.session.rollback()
			flash('Database constraint error during update.', 'danger')
			
	staff_members = Staff.query.filter_by(staff_status='Approved').all()
	return render_template('admin_trek_form.html', staff_members=staff_members, action='Edit', trek=trek)

@app.route('/admin/trek/delete/<int:trek_id>', methods=['POST'])
@login_required
def admin_delete_trek(trek_id):
	admin_required()
	try:
		trek = Trek.query.get_or_404(trek_id)
		if trek.bookings:
			trek.trek_status = 'Cancelled'
			for b in trek.bookings:
				if b.booking_status == 'Booked':
					b.booking_status = 'Trek Abandoned'
			db.session.commit()
			flash('Trek cancelled and active bookings abandoned instead of permanent deletion due to historical records.', 'warning')
		else:
			db.session.delete(trek)
			db.session.commit()
			flash('Trek permanently deleted.', 'warning')
	except Exception as e:
		db.session.rollback()
		flash('Cannot delete trek.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/trek/<int:trek_id>/book', methods=['POST'])
@login_required
def book_trek(trek_id):
	if current_user.user_role != 'trekker':
		abort(403)
		
	try:
		trek = Trek.query.filter_by(trek_id=trek_id).with_for_update().first()
		if not trek:
			abort(404)
			
		if trek.trek_status == 'Booking Open' and trek.trek_available_slots > 0:
			trek.trek_available_slots -= 1
			display_id = Booking.generate_display_id()
			new_booking = Booking(booking_display_id=display_id, user_id=current_user.user_id, trek_id=trek.trek_id, booking_status='Booked')
			db.session.add(new_booking)
			db.session.commit()
			flash('Booking successfully secured.', 'success')
		else:
			db.session.rollback()
			flash('Booking failed: Trek is full or not open.', 'danger')
	except Exception as e:
		db.session.rollback()
		flash('An internal database error interrupted your transaction.', 'danger')
		
	return redirect(url_for('dashboard'))

@app.route('/staff/trek/<int:trek_id>/update', methods=['POST'])
@login_required
def staff_update_trek(trek_id):
	if current_user.user_role != 'staff' or current_user.staff_profile.staff_status != 'Approved':
		abort(403)
		
	try:
		trek = Trek.query.get_or_404(trek_id)
		if trek.assigned_staff_id != current_user.staff_profile.staff_id:
			abort(403)
			
		slots = request.form.get('trek_available_slots')
		status = request.form.get('trek_status')
		
		if slots is not None:
			if trek.trek_status in ['Closed', 'Ongoing', 'Completed']:
				flash('Available slots cannot be modified when a trek is Closed, Ongoing, or Completed.', 'warning')
				return redirect(url_for('dashboard'))
			slots = int(slots)
			if slots < 0:
				flash('Slots cannot be negative.', 'danger')
				return redirect(url_for('dashboard'))
			trek.trek_available_slots = slots
			
		if status and status in ['Upcoming', 'Booking Open', 'Closed']:
			if trek.trek_status in ['Ongoing', 'Completed']:
				flash('Trek status cannot be modified once an expedition is Ongoing or Completed.', 'warning')
				return redirect(url_for('dashboard'))
			trek.trek_status = status
			
		db.session.commit()
		flash('Trek parameters updated.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Failed to update trek parameters.', 'danger')
		
	return redirect(url_for('dashboard'))

@app.route('/staff/trek/<int:trek_id>/resign', methods=['POST'])
@login_required
def staff_resign_trek(trek_id):
	if current_user.user_role != 'staff' or current_user.staff_profile.staff_status != 'Approved':
		abort(403)
		
	try:
		trek = Trek.query.get_or_404(trek_id)
		if trek.assigned_staff_id != current_user.staff_profile.staff_id:
			abort(403)
			
		trek.assigned_staff_id = None
		db.session.commit()
		flash('You have successfully resigned from the trek assignment.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Failed to resign from trek.', 'danger')
		
	return redirect(url_for('dashboard'))

@app.route('/treks/search', methods=['GET'])
@login_required
def search_treks():
	if current_user.user_role != 'trekker':
		abort(403)
		
	location = request.args.get('location', '')
	difficulty = request.args.get('difficulty', '')
	start_date_str = request.args.get('start_date', '')
	end_date_str = request.args.get('end_date', '')
	
	query = Trek.query.filter(Trek.trek_status.in_(['Upcoming', 'Booking Open', 'Closed', 'Ongoing', 'Completed']))
	
	if location:
		query = query.filter(Trek.trek_location.ilike(f"%{location}%"))
		
	if difficulty in ['Easy', 'Moderate', 'Hard']:
		query = query.filter_by(trek_difficulty=difficulty)
		
	if start_date_str:
		try:
			start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
			query = query.filter(Trek.trek_start_date >= start_date)
		except ValueError:
			pass
			
	if end_date_str:
		try:
			end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
			query = query.filter(Trek.trek_end_date <= end_date)
		except ValueError:
			pass
		
	results = query.all()
	return render_template('trek_search.html', treks=results, location=location, difficulty=difficulty, start_date=start_date_str, end_date=end_date_str)

@app.route('/user/profile/edit', methods=['POST'])
@login_required
def user_profile_edit():
	try:
		current_user.user_full_name = request.form.get('user_full_name')
		current_user.user_contact_no = request.form.get('user_contact_no')
		
		if current_user.user_role == 'staff' and current_user.staff_profile:
			current_user.staff_profile.staff_name = current_user.user_full_name
			current_user.staff_profile.staff_contact_details = current_user.user_contact_no
				
		db.session.commit()
		flash('Profile details updated securely.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Failed to update profile.', 'danger')
	return redirect(url_for('dashboard'))

@app.route('/user/profile/change_password', methods=['POST'])
@login_required
def user_change_password():
	old_password = request.form.get('old_password')
	new_password = request.form.get('new_password')
	confirm_password = request.form.get('confirm_password')
	
	if not old_password or not new_password or not confirm_password:
		flash('All password fields are required.', 'danger')
		return redirect(url_for('dashboard'))
		
	if not check_password_hash(current_user.user_password_hash, old_password):
		flash('Current password is incorrect.', 'danger')
		return redirect(url_for('dashboard'))
		
	if new_password != confirm_password:
		flash('New passwords do not match.', 'danger')
		return redirect(url_for('dashboard'))
		
	try:
		current_user.user_password_hash = generate_password_hash(new_password)
		db.session.commit()
		flash('Password successfully changed.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Failed to change password.', 'danger')
		
	return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
	if current_user.user_role != 'trekker':
		abort(403)
		
	try:
		booking = Booking.query.get_or_404(booking_id)
		if booking.user_id != current_user.user_id:
			abort(403)
			
		if booking.trek.trek_status != 'Booking Open':
			flash('Cannot cancel booking: Trek is no longer open for changes.', 'danger')
			return redirect(url_for('dashboard'))
			
		booking.booking_status = 'Cancelled'
		booking.trek.trek_available_slots += 1
		db.session.commit()
		flash('Booking successfully cancelled.', 'success')
	except Exception as e:
		db.session.rollback()
		flash('Failed to cancel booking.', 'danger')
	return redirect(url_for('dashboard'))

@app.route('/admin/booking/refund/<int:booking_id>', methods=['POST'])
@login_required
def admin_booking_refund(booking_id):
	admin_required()
	try:
		booking = Booking.query.get_or_404(booking_id)
		if booking.booking_status == 'Booked':
			booking.booking_status = 'Refunded'
			booking.trek.trek_available_slots += 1
			db.session.commit()
			flash(f'Booking {booking.booking_display_id} refunded securely.', 'success')
		else:
			flash('Only active bookings can be refunded.', 'warning')
	except Exception as e:
		db.session.rollback()
		flash('Failed to process refund.', 'danger')
	return redirect(url_for('admin_dashboard'))

@app.route('/trek/<int:trek_id>/review', methods=['POST'])
@login_required
def review_trek(trek_id):
	if current_user.user_role != 'trekker':
		abort(403)
		
	rating = request.form.get('rating')
	review_text = request.form.get('review_text')
	
	try:
		rating = int(rating)
		if rating < 1 or rating > 5:
			raise ValueError
			
		trek = Trek.query.get_or_404(trek_id)
		
		valid_booking = Booking.query.filter(
			Booking.user_id == current_user.user_id,
			Booking.trek_id == trek.trek_id,
			(Booking.booking_status == 'Completed') | ((Booking.booking_status == 'Booked') & (Trek.trek_status == 'Completed'))
		).first()
		
		if not valid_booking:
			flash('You can only review treks you have completed.', 'danger')
			return redirect(url_for('dashboard'))
			
		existing_review = Review.query.filter_by(
			user_id=current_user.user_id,
			trek_id=trek.trek_id
		).first()
		
		if existing_review:
			existing_review.rating = rating
			existing_review.review_text = review_text
			existing_review.created_at = datetime.now()
			flash('Your review has been updated.', 'success')
		else:
			new_review = Review(
				user_id=current_user.user_id,
				trek_id=trek.trek_id,
				rating=rating,
				review_text=review_text
			)
			db.session.add(new_review)
			flash('Thank you! Your review has been submitted.', 'success')
			
		db.session.commit()
	except ValueError:
		flash('Invalid rating submitted.', 'danger')
	except Exception as e:
		db.session.rollback()
		flash('Failed to submit review.', 'danger')
		
	return redirect(url_for('dashboard'))

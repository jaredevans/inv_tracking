# inventory/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime
from functools import wraps
from models import db, Asset, Software
from sqlalchemy import func, or_

inv_bp = Blueprint('inv', __name__, url_prefix='/inv')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('inv.login'))
        return f(*args, **kwargs)
    return decorated_function

@inv_bp.route('/')
def index():
    return redirect(url_for('inv.login'))

@inv_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == current_app.config['USERNAME'] and password == current_app.config['PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('inv.dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@inv_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('inv.login'))

@inv_bp.route('/dashboard')
@login_required
def dashboard():
    # Retrieve optional filtering parameters.
    filter_field = request.args.get('field')
    filter_value = request.args.get('value')

    # Retrieve sorting parameters.
    sortby = request.args.get('sortby')
    order = request.args.get('order', 'asc')  # Default to ascending

    # Retrieve the search term from the query parameter
    search_term = request.args.get('search')

    query = Asset.query

    # Apply filtering if a valid filter is provided.
    allowed_filters = ['category', 'physical_location', 'department']
    if filter_field and filter_value and filter_field in allowed_filters:
        query = query.filter(getattr(Asset, filter_field) == filter_value)

    # Apply wildcard search for the specified fields if search term provided.
    if search_term:
        like_pattern = f"%{search_term.lower()}%"
        query = query.outerjoin(Asset.software_packages).filter(
            or_(
                func.lower(Asset.asset_tag).like(like_pattern),
                func.lower(Asset.asset_name).like(like_pattern),
                func.lower(Asset.physical_location).like(like_pattern),
                func.lower(Asset.department).like(like_pattern),
                func.lower(Asset.description).like(like_pattern),
                func.lower(Software.software_name).like(like_pattern)
            )
        ).distinct()

    # Apply case-insensitive sorting if a valid sort field is provided.
    allowed_sort_fields = ['asset_tag', 'asset_name', 'category', 'physical_location', 'department']
    if sortby in allowed_sort_fields:
        column = getattr(Asset, sortby)
        if order == 'desc':
            query = query.order_by(func.lower(column).desc())
        else:
            query = query.order_by(func.lower(column).asc())

    assets = query.all()
    return render_template('dashboard.html', assets=assets, search_term=search_term)

@inv_bp.route('/asset/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def view_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        asset.asset_tag = request.form.get('asset_tag')
        asset.asset_name = request.form.get('asset_name')
        asset.category = request.form.get('category')
        asset.description = request.form.get('description')
        asset.serial_number = request.form.get('serial_number')
        asset.operating_system = request.form.get('operating_system')
        asset.ip_address = request.form.get('ip_address')
        asset.mac_address = request.form.get('mac_address')
        asset.configuration_details = request.form.get('configuration_details')
        asset.purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d') if request.form.get('purchase_date') else None
        asset.vendor = request.form.get('vendor')
        asset.physical_location = request.form.get('physical_location')
        asset.department = request.form.get('department')
        asset.assigned_to = request.form.get('assigned_to')
        asset.status = request.form.get('status')
        asset.data_classification = request.form.get('data_classification')
        asset.data_types = request.form.get('data_types')
        asset.data_storage_location = request.form.get('data_storage_location')
        asset.data_processing_activities = request.form.get('data_processing_activities')
        db.session.commit()
        flash('Asset updated successfully!')
        return redirect(url_for('inv.dashboard'))
    return render_template('asset_detail.html', asset=asset)

@inv_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    if request.method == 'POST':
        new_asset = Asset(
            asset_tag=request.form.get('asset_tag'),
            asset_name=request.form.get('asset_name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            serial_number=request.form.get('serial_number'),
            operating_system=request.form.get('operating_system'),
            ip_address=request.form.get('ip_address'),
            mac_address=request.form.get('mac_address'),
            configuration_details=request.form.get('configuration_details'),
            purchase_date=datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d') if request.form.get('purchase_date') else None,
            vendor=request.form.get('vendor'),
            physical_location=request.form.get('physical_location'),
            department=request.form.get('department'),
            assigned_to=request.form.get('assigned_to'),
            status=request.form.get('status'),
            data_classification=request.form.get('data_classification'),
            data_types=request.form.get('data_types'),
            data_storage_location=request.form.get('data_storage_location'),
            data_processing_activities=request.form.get('data_processing_activities')
        )
        db.session.add(new_asset)
        db.session.commit()
        flash('New asset added successfully!')
        return redirect(url_for('inv.dashboard'))
    return render_template('add_asset.html')

@inv_bp.route('/asset/<int:asset_id>/add_software', methods=['GET', 'POST'])
@login_required
def add_software(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        new_software = Software(
            asset_id=asset.id,
            software_name=request.form.get('software_name'),
            version=request.form.get('version'),
            license_info=request.form.get('license_info'),
            vendor=request.form.get('vendor'),
            configuration_details=request.form.get('configuration_details')
        )
        db.session.add(new_software)
        db.session.commit()
        flash('Software package added successfully!')
        return redirect(url_for('inv.view_asset', asset_id=asset.id))
    return render_template('add_software.html', asset=asset)

@inv_bp.route('/software/<int:software_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_software(software_id):
    software = Software.query.get_or_404(software_id)
    if request.method == 'POST':
        software.software_name = request.form.get('software_name')
        software.version = request.form.get('version')
        software.license_info = request.form.get('license_info')
        software.vendor = request.form.get('vendor')
        software.configuration_details = request.form.get('configuration_details')
        db.session.commit()
        flash('Software package updated successfully!')
        return redirect(url_for('inv.view_asset', asset_id=software.asset_id))
    return render_template('edit_software.html', software=software)

# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(100))
    asset_name = db.Column(db.String(200))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)

    # Removed fields: manufacturer, model, cost, warranty_expiration,
    # acquisition_method, maintenance_history, depreciation_details, end_of_life,
    # data_volume, data_retention_policy, compliance_details

    # Retained technical fields:
    serial_number = db.Column(db.String(200))
    operating_system = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    mac_address = db.Column(db.String(50))
    configuration_details = db.Column(db.Text)

    purchase_date = db.Column(db.Date)
    vendor = db.Column(db.String(200))
    physical_location = db.Column(db.String(200))
    department = db.Column(db.String(200))
    assigned_to = db.Column(db.String(200))
    
    # Retained lifecycle and data categorization fields:
    status = db.Column(db.String(50))
    data_classification = db.Column(db.String(100))     # e.g., Public, Internal, Confidential, Regulated
    data_types = db.Column(db.String(200))              # e.g., PII, Research Data, Financial Data
    data_storage_location = db.Column(db.String(200))   # e.g., "Local Server", "Cloud"
    data_processing_activities = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    software_packages = db.relationship('Software', backref='asset', lazy=True)

class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    software_name = db.Column(db.String(200))
    version = db.Column(db.String(100))
    # Removed installation_date and patch_history
    license_info = db.Column(db.String(200))
    vendor = db.Column(db.String(200))
    configuration_details = db.Column(db.Text)


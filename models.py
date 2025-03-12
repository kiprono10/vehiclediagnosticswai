from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for authentication (if needed in future)"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to emission records
    emission_records = db.relationship('EmissionRecord', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'

class CarBrand(db.Model):
    """Model for car brands data"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    logo_url = db.Column(db.String(256), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<CarBrand {self.name}>'

class EmissionRecord(db.Model):
    """Model for storing emission prediction records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    vehicle_type = db.Column(db.String(64), nullable=False)
    fuel_type = db.Column(db.String(64), nullable=False)
    engine_size = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    co2_emissions = db.Column(db.Float, nullable=False)
    nox_emissions = db.Column(db.Float, nullable=True)
    pm_emissions = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmissionRecord {self.id} - {self.vehicle_type}>'

class ChatHistory(db.Model):
    """Model for storing chat interactions (optional)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    issue_category = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.id}>'

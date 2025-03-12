import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from chatbot import diagnose_issue
from emissions_predictor import predict_emissions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///auto_advisor.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the database extension
db.init_app(app)

# Import models and create tables
with app.app_context():
    from models import User, CarBrand, EmissionRecord
    db.create_all()
    
    # Initialize car brands if they don't exist
    if not CarBrand.query.first():
        brands = [
            "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", 
            "Volkswagen", "BMW", "Mercedes-Benz", "Audi", "Hyundai",
            "Kia", "Subaru", "Mazda", "Lexus", "Tesla"
        ]
        for brand_name in brands:
            brand = CarBrand(name=brand_name)
            db.session.add(brand)
        db.session.commit()
        logger.info("Initialized car brands")

# Define routes
@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/emissions')
def emissions():
    """Emissions prediction page route"""
    brands = CarBrand.query.all()
    return render_template('emissions.html', brands=brands)

@app.route('/predict_emissions', methods=['POST'])
def process_emissions():
    """API endpoint for emissions prediction"""
    try:
        data = request.form
        vehicle_type = data.get('vehicle_type')
        fuel_type = data.get('fuel_type')
        engine_size = float(data.get('engine_size', 0))
        year = int(data.get('year', 0))
        
        emissions_data = predict_emissions(vehicle_type, fuel_type, engine_size, year)
        
        # Store the prediction in the database
        new_record = EmissionRecord(
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            engine_size=engine_size,
            year=year,
            co2_emissions=emissions_data['co2'],
            nox_emissions=emissions_data['nox'],
            pm_emissions=emissions_data['pm']
        )
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify(emissions_data)
    except Exception as e:
        logger.error(f"Error in emissions prediction: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/chatbot')
def chatbot():
    """Chatbot page route"""
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot interactions"""
    try:
        user_message = request.form.get('message', '')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process the message with the diagnostic system
        response = diagnose_issue(user_message)
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route('/car_info')
def car_info():
    """Car information page route"""
    return render_template('car_info.html')

@app.route('/maintenance')
def maintenance():
    """Car maintenance page route"""
    brands = CarBrand.query.all()
    return render_template('maintenance.html', brands=brands)

@app.route('/brands')
def brands():
    """Car brands comparison page route"""
    brands = CarBrand.query.all()
    return render_template('brands.html', brands=brands)

@app.route('/technologies')
def technologies():
    """Upcoming car technologies page route"""
    return render_template('technologies.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error="Server error. Please try again later."), 500

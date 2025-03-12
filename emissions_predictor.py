import logging
import math
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base emission factors (g/km) for different vehicle and fuel types
EMISSION_FACTORS = {
    'sedan': {
        'petrol': {'co2': 120, 'nox': 0.06, 'pm': 0.005},
        'diesel': {'co2': 110, 'nox': 0.50, 'pm': 0.025},
        'hybrid': {'co2': 90, 'nox': 0.04, 'pm': 0.003},
        'electric': {'co2': 0, 'nox': 0, 'pm': 0}
    },
    'suv': {
        'petrol': {'co2': 180, 'nox': 0.08, 'pm': 0.007},
        'diesel': {'co2': 160, 'nox': 0.70, 'pm': 0.035},
        'hybrid': {'co2': 120, 'nox': 0.05, 'pm': 0.004},
        'electric': {'co2': 0, 'nox': 0, 'pm': 0}
    },
    'truck': {
        'petrol': {'co2': 250, 'nox': 0.10, 'pm': 0.010},
        'diesel': {'co2': 220, 'nox': 0.90, 'pm': 0.045},
        'hybrid': {'co2': 180, 'nox': 0.07, 'pm': 0.006},
        'electric': {'co2': 0, 'nox': 0, 'pm': 0}
    },
    'compact': {
        'petrol': {'co2': 100, 'nox': 0.05, 'pm': 0.004},
        'diesel': {'co2': 90, 'nox': 0.40, 'pm': 0.020},
        'hybrid': {'co2': 70, 'nox': 0.03, 'pm': 0.002},
        'electric': {'co2': 0, 'nox': 0, 'pm': 0}
    }
}

# Year factors for emission improvement
# Represents technological improvements over time
def get_year_factor(year):
    """Calculate emission reduction factor based on vehicle year"""
    current_year = 2023
    if year >= current_year:
        return 0.9  # Newest vehicles
    elif year >= 2018:
        return 1.0  # Recent vehicles
    elif year >= 2010:
        return 1.2  # Last decade
    elif year >= 2000:
        return 1.5  # Early 2000s
    else:
        return 2.0  # Older vehicles
        
# Engine size factor
def get_engine_size_factor(engine_size, fuel_type):
    """Calculate emission factor based on engine size and fuel type"""
    if fuel_type == 'electric':
        return 1.0  # Electric vehicles aren't affected by engine size
        
    if engine_size <= 1.0:
        return 0.8
    elif engine_size <= 1.6:
        return 1.0
    elif engine_size <= 2.0:
        return 1.2
    elif engine_size <= 3.0:
        return 1.5
    else:
        return 2.0

def predict_emissions(vehicle_type, fuel_type, engine_size, year):
    """
    Predict vehicle emissions based on various factors
    
    Args:
        vehicle_type (str): Type of vehicle (sedan, suv, truck, compact)
        fuel_type (str): Type of fuel (petrol, diesel, hybrid, electric)
        engine_size (float): Engine size in liters
        year (int): Year of manufacture
        
    Returns:
        dict: Predicted CO2, NOx, and PM emissions
    """
    try:
        # Default to sedan if vehicle type not found
        if vehicle_type.lower() not in EMISSION_FACTORS:
            vehicle_type = "sedan"
            logger.warning(f"Unknown vehicle type, defaulting to sedan")
            
        # Default to petrol if fuel type not found
        if fuel_type.lower() not in EMISSION_FACTORS[vehicle_type.lower()]:
            fuel_type = "petrol"
            logger.warning(f"Unknown fuel type, defaulting to petrol")
        
        # Get base emission factors for the vehicle and fuel type
        base_emissions = EMISSION_FACTORS[vehicle_type.lower()][fuel_type.lower()]
        
        # Calculate modifiers
        year_factor = get_year_factor(year)
        engine_factor = get_engine_size_factor(engine_size, fuel_type.lower())
        
        # Calculate final emissions
        co2 = base_emissions['co2'] * year_factor * engine_factor
        nox = base_emissions['nox'] * year_factor * engine_factor
        pm = base_emissions['pm'] * year_factor * engine_factor
        
        # Add some minor random variation (±5%)
        variation = lambda x: x * (1 + (random.random() - 0.5) / 10)
        
        # Return calculated emissions
        return {
            'co2': round(variation(co2), 1),  # g/km
            'nox': round(variation(nox), 3),  # g/km
            'pm': round(variation(pm), 4),    # g/km
            'rating': calculate_emissions_rating(co2, nox, pm),
            'recommendations': generate_recommendations(vehicle_type, fuel_type, engine_size, year)
        }
    
    except Exception as e:
        logger.error(f"Error in predict_emissions: {str(e)}")
        # Return default values in case of error
        return {
            'co2': 150.0,
            'nox': 0.2,
            'pm': 0.01,
            'rating': 'C',
            'recommendations': ['Unable to generate specific recommendations due to an error.']
        }

def calculate_emissions_rating(co2, nox, pm):
    """Calculate an overall emissions rating from A to F"""
    # Weighted scoring system
    score = co2/100 + nox*10 + pm*100
    
    if score < 1:
        return 'A'
    elif score < 1.5:
        return 'B'
    elif score < 2.5:
        return 'C'
    elif score < 4:
        return 'D'
    elif score < 6:
        return 'E'
    else:
        return 'F'

def generate_recommendations(vehicle_type, fuel_type, engine_size, year):
    """Generate recommendations to improve emissions"""
    recommendations = []
    
    # General recommendations that apply to all vehicles
    general_recommendations = [
        "Maintain proper tire pressure to reduce rolling resistance",
        "Remove excess weight from your vehicle",
        "Use recommended grade of motor oil",
        "Avoid excessive idling",
        "Plan and combine trips to reduce cold starts"
    ]
    
    # Add 2-3 general recommendations
    recommendations.extend(random.sample(general_recommendations, min(3, len(general_recommendations))))
    
    # Add specific recommendations based on vehicle attributes
    if fuel_type.lower() != 'electric':
        recommendations.append("Consider regular engine tune-ups for optimal efficiency")
        
        if year < 2010:
            recommendations.append("Newer vehicles have significantly better emissions controls")
        
        if engine_size > 2.0:
            recommendations.append("Consider downsizing to a vehicle with a smaller engine for better efficiency")
            
        if fuel_type.lower() == 'petrol' and year >= 2010:
            recommendations.append("Modern diesel or hybrid vehicles may offer better emissions performance")
    
    # Limit to 5 recommendations
    return recommendations[:5]

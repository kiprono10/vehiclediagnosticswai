import re
import logging
import random
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define vehicle problem categories
CATEGORIES = {
    'engine': ['engine', 'motor', 'misfire', 'knocking', 'stalling', 'power', 'performance', 'rpm', 'acceleration', 'idle', 'start', 'turnover'],
    'transmission': ['transmission', 'gear', 'shifting', 'clutch', 'gearbox', 'automatic', 'manual', 'slipping', 'grinding'],
    'brakes': ['brakes', 'stopping', 'pedal', 'abs', 'brake pad', 'rotor', 'squeal', 'grinding', 'stopping distance'],
    'electrical': ['battery', 'electrical', 'light', 'headlight', 'alternator', 'fuse', 'spark', 'ignition', 'starter', 'radio', 'dashboard', 'computer', 'sensor'],
    'fuel': ['fuel', 'gas', 'mileage', 'consumption', 'economy', 'mpg', 'efficiency', 'tank', 'petrol', 'diesel', 'injector'],
    'cooling': ['overheat', 'temperature', 'cooling', 'radiator', 'coolant', 'thermostat', 'fan', 'water pump', 'heat'],
    'suspension': ['suspension', 'shock', 'strut', 'bouncing', 'spring', 'ride', 'handling', 'steering', 'alignment', 'wheel', 'tire', 'tyre', 'flat'],
    'exhaust': ['exhaust', 'emissions', 'smoke', 'smog', 'muffler', 'catalytic', 'converter', 'pipe', 'noise'],
    'oil': ['oil', 'leak', 'lubrication', 'pressure', 'synthetic', 'change', 'viscosity', 'level', 'consumption'],
    'general': []  # Fallback category
}

# Knowledge base for common issues and solutions
KNOWLEDGE_BASE = {
    'engine': {
        'issues': [
            {
                'problem': 'Engine not starting',
                'causes': ['Dead battery', 'Faulty starter', 'Fuel delivery problem', 'Ignition system issue'],
                'symptoms': ['Click sound when turning key', 'No sound when turning key', 'Engine cranks but doesn\'t start'],
                'solutions': ['Check battery connections', 'Test battery voltage', 'Inspect starter', 'Check fuel pump and injectors'],
                'mechanic_visit': 'Maybe - Depends on your diagnostic skills and the specific cause'
            },
            {
                'problem': 'Engine misfiring',
                'causes': ['Faulty spark plugs', 'Bad ignition coils', 'Clogged fuel injectors', 'Vacuum leak'],
                'symptoms': ['Rough idle', 'Hesitation when accelerating', 'Reduced power', 'Check engine light'],
                'solutions': ['Replace spark plugs', 'Check ignition coils', 'Clean fuel injectors', 'Check for vacuum leaks'],
                'mechanic_visit': 'Maybe - If replacing spark plugs doesn\'t solve the issue'
            },
            {
                'problem': 'Engine overheating',
                'causes': ['Low coolant level', 'Faulty thermostat', 'Bad water pump', 'Radiator issues'],
                'symptoms': ['Temperature gauge reading high', 'Steam from hood', 'Engine power loss'],
                'solutions': ['Check coolant level', 'Inspect cooling system for leaks', 'Test thermostat', 'Check water pump'],
                'mechanic_visit': 'Yes - Overheating can cause serious engine damage if not addressed quickly'
            }
        ]
    },
    'transmission': {
        'issues': [
            {
                'problem': 'Transmission slipping',
                'causes': ['Low transmission fluid', 'Worn clutch', 'Faulty solenoids', 'Internal wear'],
                'symptoms': ['Engine revs but car doesn\'t accelerate properly', 'Unexpected gear changes', 'Delays in acceleration'],
                'solutions': ['Check transmission fluid level and condition', 'Inspect clutch (manual transmission)', 'Scan for trouble codes'],
                'mechanic_visit': 'Yes - Transmission issues usually require professional diagnosis'
            },
            {
                'problem': 'Hard shifting',
                'causes': ['Low transmission fluid', 'Faulty shift solenoid', 'Clutch problems', 'Transmission control module issues'],
                'symptoms': ['Difficulty changing gears', 'Grinding noise when shifting', 'Delayed engagement'],
                'solutions': ['Check transmission fluid', 'Inspect clutch pedal free play (manual)', 'Scan for trouble codes'],
                'mechanic_visit': 'Yes - Most transmission issues require professional service'
            }
        ]
    },
    'brakes': {
        'issues': [
            {
                'problem': 'Squeaking or squealing brakes',
                'causes': ['Worn brake pads', 'Glazed pads or rotors', 'Lack of lubrication on backing plates'],
                'symptoms': ['High-pitched noise when braking', 'Noise disappears when brakes are applied firmly'],
                'solutions': ['Inspect brake pad thickness', 'Check for uneven wear', 'Apply brake lubricant to appropriate parts'],
                'mechanic_visit': 'Maybe - Brake pad replacement can be DIY but requires proper tools and knowledge'
            },
            {
                'problem': 'Spongy brake pedal',
                'causes': ['Air in brake lines', 'Brake fluid leak', 'Faulty master cylinder', 'Failing brake booster'],
                'symptoms': ['Brake pedal feels soft', 'Pedal goes closer to floor than usual', 'Reduced braking effectiveness'],
                'solutions': ['Check brake fluid level', 'Inspect for leaks', 'Bleed brake system'],
                'mechanic_visit': 'Yes - Brake system issues affecting performance are safety critical'
            }
        ]
    },
    'electrical': {
        'issues': [
            {
                'problem': 'Battery not holding charge',
                'causes': ['Old battery', 'Faulty alternator', 'Parasitic drain', 'Loose connections'],
                'symptoms': ['Difficulty starting', 'Headlights dim when idle', 'Battery warning light on dashboard'],
                'solutions': ['Test battery voltage', 'Check alternator output', 'Look for parasitic draws', 'Clean battery terminals'],
                'mechanic_visit': 'No - Battery testing and replacement is usually simple'
            },
            {
                'problem': 'Lights not working properly',
                'causes': ['Blown bulbs', 'Bad fuse', 'Wiring issue', 'Switch malfunction'],
                'symptoms': ['Lights don\'t turn on', 'Intermittent operation', 'Dimming'],
                'solutions': ['Check and replace bulbs', 'Inspect fuses', 'Test switches', 'Look for wiring damage'],
                'mechanic_visit': 'No - Most light issues are user serviceable'
            }
        ]
    },
    'fuel': {
        'issues': [
            {
                'problem': 'Poor fuel economy',
                'causes': ['Clogged air filter', 'Faulty oxygen sensor', 'Bad spark plugs', 'Incorrect tire pressure'],
                'symptoms': ['More frequent refueling', 'Reduced range', 'Higher fuel costs'],
                'solutions': ['Replace air filter', 'Check and correct tire pressure', 'Inspect spark plugs', 'Scan for sensor issues'],
                'mechanic_visit': 'No - Many fuel economy issues can be addressed with basic maintenance'
            },
            {
                'problem': 'Fuel smell',
                'causes': ['Fuel line leak', 'Loose gas cap', 'Faulty EVAP system', 'Injector leaks'],
                'symptoms': ['Gasoline odor', 'Visible leaks', 'Check engine light'],
                'solutions': ['Check gas cap', 'Inspect fuel lines', 'Look for visible leaks'],
                'mechanic_visit': 'Yes - Fuel leaks are a fire hazard and should be addressed immediately'
            }
        ]
    },
    'cooling': {
        'issues': [
            {
                'problem': 'Coolant leak',
                'causes': ['Radiator crack', 'Loose hose clamp', 'Blown head gasket', 'Bad water pump'],
                'symptoms': ['Low coolant level', 'Puddles under car', 'Sweet smell', 'Overheating'],
                'solutions': ['Check all hoses and connections', 'Pressure test cooling system', 'Inspect radiator'],
                'mechanic_visit': 'Yes - Cooling system issues can lead to engine damage'
            }
        ]
    },
    'suspension': {
        'issues': [
            {
                'problem': 'Bouncy ride',
                'causes': ['Worn shock absorbers', 'Damaged springs', 'Loose components'],
                'symptoms': ['Car bounces excessively after bumps', 'Dipping when braking', 'Swaying during turns'],
                'solutions': ['Inspect shocks for leaks', 'Check springs for damage', 'Tighten all suspension components'],
                'mechanic_visit': 'Yes - Suspension work usually requires special tools and knowledge'
            },
            {
                'problem': 'Uneven tire wear',
                'causes': ['Misalignment', 'Improper inflation', 'Worn suspension components', 'Balancing issues'],
                'symptoms': ['Tires wearing on inside/outside edges', 'Steering wheel vibration', 'Car pulls to one side'],
                'solutions': ['Check tire pressure', 'Rotate tires', 'Get wheel alignment', 'Balance wheels'],
                'mechanic_visit': 'Yes - Alignment requires specialized equipment'
            }
        ]
    },
    'exhaust': {
        'issues': [
            {
                'problem': 'Loud exhaust',
                'causes': ['Hole in muffler', 'Broken exhaust pipe', 'Damaged catalytic converter', 'Exhaust leak at joint'],
                'symptoms': ['Increased noise', 'Rumbling sound', 'Hissing near engine'],
                'solutions': ['Inspect entire exhaust system', 'Look for rust, holes or damaged parts'],
                'mechanic_visit': 'Yes - Exhaust repairs often require welding or special tools'
            }
        ]
    },
    'oil': {
        'issues': [
            {
                'problem': 'Oil leak',
                'causes': ['Loose oil filter', 'Bad gasket', 'Worn seals', 'Oil pan damage'],
                'symptoms': ['Oil spots where car is parked', 'Burning smell', 'Low oil level', 'Oil pressure warning'],
                'solutions': ['Check oil level', 'Inspect for visible leaks', 'Tighten oil filter', 'Consider using stop-leak additive for minor leaks'],
                'mechanic_visit': 'Maybe - Depends on the source and severity of the leak'
            }
        ]
    },
    'general': {
        'issues': [
            {
                'problem': 'Check engine light on',
                'causes': ['Various sensor issues', 'Emissions problems', 'Engine misfires', 'Loose gas cap'],
                'symptoms': ['Warning light on dashboard', 'Possible performance issues', 'Failed emissions test'],
                'solutions': ['Check gas cap', 'Use OBD-II scanner to read codes', 'Address specific issue indicated by code'],
                'mechanic_visit': 'Maybe - Depends on the specific code and your comfort level with repairs'
            }
        ]
    }
}

def diagnose_issue(user_input):
    """
    Process user input and return a diagnostic response
    
    Args:
        user_input (str): User's description of their car problem
        
    Returns:
        str: Diagnostic response with possible causes and solutions
    """
    try:
        # Convert input to lowercase for better matching
        user_input = user_input.lower()
        
        # Remove any special characters
        user_input = re.sub(r'[^\w\s]', ' ', user_input)
        
        # Score categories based on keyword matches
        category_scores = defaultdict(int)
        for category, keywords in CATEGORIES.items():
            for keyword in keywords:
                if keyword in user_input:
                    category_scores[category] += 1
        
        # If no matches found, use general category
        if not category_scores:
            category = 'general'
        else:
            # Get the category with the highest score
            category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        logger.debug(f"Diagnosed category: {category}")
        
        # Get issues for the identified category
        category_issues = KNOWLEDGE_BASE.get(category, KNOWLEDGE_BASE['general'])['issues']
        
        # Find the most relevant issue
        best_match = None
        best_match_score = 0
        
        for issue in category_issues:
            score = 0
            # Check problem keywords
            if any(keyword in user_input for keyword in issue['problem'].lower().split()):
                score += 2
            
            # Check symptoms
            for symptom in issue['symptoms']:
                if any(keyword in user_input for keyword in symptom.lower().split()):
                    score += 1
            
            if score > best_match_score:
                best_match_score = score
                best_match = issue
        
        # If no good match, pick a random issue from the category
        if best_match is None or best_match_score == 0:
            if category_issues:
                best_match = random.choice(category_issues)
            else:
                # Fallback response if no issues found
                return "I'm not sure about this specific issue. Could you provide more details about the symptoms you're experiencing with your vehicle?"
        
        # Format response
        response = f"Based on your description, you may be experiencing: **{best_match['problem']}**\n\n"
        
        response += "**Possible causes:**\n"
        for cause in best_match['causes']:
            response += f"- {cause}\n"
        
        response += "\n**Typical symptoms:**\n"
        for symptom in best_match['symptoms']:
            response += f"- {symptom}\n"
        
        response += "\n**Recommended solutions:**\n"
        for solution in best_match['solutions']:
            response += f"- {solution}\n"
        
        response += f"\n**Should you visit a mechanic?** {best_match['mechanic_visit']}"
        
        return response
    
    except Exception as e:
        logger.error(f"Error in diagnose_issue: {str(e)}")
        return "I'm sorry, I encountered an error while diagnosing your issue. Please try describing your problem again."

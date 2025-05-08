import datetime
import json
import os
import logging
from pathlib import Path
import swisseph as swe

# Constants
OUTPUT_DIR = r"D:\AI\nebles\database\embedding_processor"
EPHEMERIS_PATH = r"./ephemeris"  # Adjust to your ephemeris file directory

# Aspect types and their properties (angle, orb)
ASPECT_TYPES = {
    'conjunction': (0, 10),
    'semisextile': (30, 2),
    'sextile': (60, 6),
    'square': (90, 8),
    'trine': (120, 8),
    'quincunx': (150, 2),
    'opposition': (180, 10)
}

# Zodiac signs and their corresponding rulers
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 
                'Leo', 'Virgo', 'Libra', 'Scorpio', 
                'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Map zodiac signs to their ruling planets
ZODIAC_RULERS = {
    'Aries': 'Mars',
    'Taurus': 'Venus',
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': 'Pluto',
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': 'Uranus',
    'Pisces': 'Neptune'
}

# Celestial bodies to calculate
BODIES = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
    'North Node': swe.TRUE_NODE,
    'South Node': None,  # Calculated as 180° opposite North Node
    'Chiron': swe.CHIRON,
    'Ceres': swe.CERES,
    'Pallas': swe.PALLAS,
    'Juno': swe.JUNO,
    'Vesta': swe.VESTA
}

def clear_folder(folder_path):
    """Clear all contents in the specified folder."""
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        logging.info(f"Cleared directory: {folder_path}")
    except Exception as e:
        logging.error(f"Error clearing directory {folder_path}: {e}")

def get_zodiac_sign(degree):
    """Convert zodiac degree to sign."""
    degree = degree % 360
    if 0 <= degree < 30: return 'Aries'
    elif 30 <= degree < 60: return 'Taurus'
    elif 60 <= degree < 90: return 'Gemini'
    elif 90 <= degree < 120: return 'Cancer'
    elif 120 <= degree < 150: return 'Leo'
    elif 150 <= degree < 180: return 'Virgo'
    elif 180 <= degree < 210: return 'Libra'
    elif 210 <= degree < 240: return 'Scorpio'
    elif 240 <= degree < 270: return 'Sagittarius'
    elif 270 <= degree < 300: return 'Capricorn'
    elif 300 <= degree < 330: return 'Aquarius'
    else: return 'Pisces'

def get_house(degree, house_cusps):
    """Determine house placement for a given degree."""
    degree = degree % 360
    for i in range(12):
        start_cusp = house_cusps[i] % 360
        end_cusp = house_cusps[(i + 1) % 12] % 360
        if end_cusp <= start_cusp:
            end_cusp += 360
        if start_cusp <= degree < end_cusp or (degree + 360) < end_cusp:
            return i + 1
    return 1  # Default to 1st house if calculation fails

def get_planet_positions(now, longitude=None, latitude=None, time_provided=False):
    """Calculate positions, signs, retrograde status, aspects, and houses (if applicable)."""
    try:
        # Set ephemeris path
        swe.set_ephe_path(EPHEMERIS_PATH)
        
        # Convert datetime to Julian Day
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
        
        # Initialize data structures
        positions = {}
        planet_signs = {}
        planet_retrograde = {}
        houses = None
        house_cusps = None
        
        # Calculate positions for each body
        for body_name, body_id in BODIES.items():
            if body_name == 'South Node':
                # South Node is 180° opposite North Node
                north_node_pos = positions['North Node']['longitude']
                south_node_pos = (north_node_pos + 180) % 360
                positions['South Node'] = {
                    'longitude': south_node_pos,
                    'degree': south_node_pos % 30,
                    'minute': (south_node_pos % 1) * 60
                }
                planet_signs['South Node'] = get_zodiac_sign(south_node_pos)
                planet_retrograde['South Node'] = planet_retrograde['North Node']
                continue
                
            # Calculate position
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            ret, pos = swe.calc_ut(jd, body_id, flags)
            
            longitude_deg = pos[0]
            speed = pos[3]  # Speed in longitude (degrees/day)
            
            positions[body_name] = {
                'longitude': longitude_deg,
                'degree': longitude_deg % 30,
                'minute': (longitude_deg % 1) * 60
            }
            planet_signs[body_name] = get_zodiac_sign(longitude_deg)
            planet_retrograde[body_name] = speed < 0
        
        # Calculate houses if time and location are provided
        if time_provided and longitude is not None and latitude is not None:
            house_cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')  # Placidus houses
            houses = {body_name: get_house(pos['longitude'], house_cusps) for body_name, pos in positions.items()}
        
        # Calculate aspects
        aspects = []
        body_names = list(positions.keys())
        for i in range(len(body_names)):
            for j in range(i + 1, len(body_names)):
                body1 = body_names[i]
                body2 = body_names[j]
                angle = abs((positions[body1]['longitude'] - positions[body2]['longitude']) % 360)
                if angle > 180:
                    angle = 360 - angle
                
                for aspect_name, (target, orb) in ASPECT_TYPES.items():
                    if abs(angle - target) <= orb:
                        aspects.append({
                            'body1': body1,
                            'body2': body2,
                            'aspect': aspect_name,
                            'angle': round(angle, 2),
                            'sign1': planet_signs[body1],
                            'sign2': planet_signs[body2]
                        })
        
        logging.info("Calculated positions, signs, retrograde status, aspects, and houses (if applicable)")
        return positions, planet_signs, planet_retrograde, aspects, houses, house_cusps
        
    except Exception as e:
        logging.error(f"Error calculating positions: {e}")
        raise

def save_planet_data(positions, planet_signs, planet_retrograde, aspects, houses, house_cusps, now, output_dir):
    """Create and save a single JSON file with data for all zodiac signs."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        time_utc = now.isoformat() + 'Z'
        data = {
            "time_utc": time_utc,
            "data": {},
            "zodiac_rulers": ZODIAC_RULERS
        }
        
        # Generate data for each zodiac sign
        for sign in ZODIAC_SIGNS:
            data["data"][sign] = {
                "zodiac_sign": sign,
                "focus_planet": ZODIAC_RULERS[sign],
                "positions": {
                    body: {
                        "longitude": round(pos['longitude'], 6),
                        "degree": round(pos['degree'], 6),
                        "minute": round(pos['minute'], 2),
                        "zodiac": planet_signs[body],
                        "retrograde": planet_retrograde[body],
                        "house": houses.get(body) if houses else None
                    } for body, pos in positions.items()
                },
                "aspects": aspects,
                "house_cusps": [round(cusp, 6) for cusp in house_cusps] if house_cusps else None
            }
        
        # Save to a single JSON file
        date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"planet_positions_{date_time_str}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
        logging.info(f"Saved planetary data to {filepath}")
        return data
        
    except Exception as e:
        logging.error(f"Error saving planetary data: {e}")
        raise

def main(longitude=None, latitude=None, time_provided=False):
    """Main execution function to generate, save, and return planetary data."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Clear output directory
        clear_folder(OUTPUT_DIR)
        
        # Calculate planetary positions
        now = datetime.datetime.now()
        positions, planet_signs, planet_retrograde, aspects, houses, house_cusps = get_planet_positions(
            now, longitude, latitude, time_provided
        )
        
        # Save and return data
        result = save_planet_data(
            positions,
            planet_signs,
            planet_retrograde,
            aspects,
            houses,
            house_cusps,
            now,
            OUTPUT_DIR
        )
        
        logging.info("Planetary data generation, saving, and JSON return completed successfully")
        return result
        
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise

if __name__ == "__main__":
    # Example: Run with time and location for full calculations
    # result = main(longitude=0.0, latitude=51.5, time_provided=True)
    # print(json.dumps(result, indent=4))
    
    # Run without time/location for zodiac positions and aspects only
    result = main()
    print(json.dumps(result, indent=4))
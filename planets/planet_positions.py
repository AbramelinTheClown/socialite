import datetime
import json
import os
from pathlib import Path
import logging
import numpy as np
import ollama

# Constants for directory paths
INPUT_DIR = r"D:\AI\nebles\planets\planet-alignments"
OUTPUT_DIR = r"D:\AI\nebles\planets\output_horoscopes"

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

# Aspect properties for calculation
ASPECT_PROPS = {
    'conjunction': {'angle': 0, 'orb': 10},
    'semisextile': {'angle': 30, 'orb': 2},
    'sextile': {'angle': 60, 'orb': 6},
    'square': {'angle': 90, 'orb': 8},
    'trine': {'angle': 120, 'orb': 8},
    'quincunx': {'angle': 150, 'orb': 2},
    'opposition': {'angle': 180, 'orb': 10}
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

def get_planet_positions(now):
    """Calculate planetary positions, signs, retrograde status, and aspects."""
    try:
        # Calculate astronomical data for each planet
        # (Note: This is a simplified representation and would require actual 
        # astronomical calculations or an API in a real implementation)
        
        # Mock data generation for demonstration purposes
        cartesian_positions = {
            'Mercury': {'x': np.random.rand(), 'y': np.random.rand(), 'z': np.random.rand()},
            'Venus': {'x': np.random.rand(), 'y': np.random.rand(), 'z': np.random.rand()},
            # ... other planets ...
        }
        
        planet_signs = {
            'Mercury': 'Aries',
            'Venus': 'Taurus',
            # ... other planets ...
        }
        
        planet_retrograde = {
            'Mercury': False,
            'Venus': False,
            # ... other planets ...
        }
        
        aspects = []
        
        # Calculate aspects between all pairs of planets
        for i in range(len(planet_signs)):
            for j in range(i + 1, len(planet_signs)):
                planet1 = list(planet_signs.keys())[i]
                planet2 = list(planet_signs.keys())[j]
                
                # Calculate the angle between the two planets
                angle = abs(np.random.rand() * 360)
                
                for aspect_name in ASPECT_TYPES:
                    target, orb = ASPECT_TYPES[aspect_name]
                    if abs(angle - target) <= orb:
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_name,
                            'angle': round(angle, 2),
                            'sign1': planet_signs[planet1],
                            'sign2': planet_signs[planet2]
                        })
        
        logging.info("Calculated planetary positions, signs, retrograde status, and aspects")
        return cartesian_positions, planet_signs, planet_retrograde, aspects
        
    except Exception as e:
        logging.error(f"Error calculating positions: {e}")
        raise

def save_planet_positions(cartesian_positions, planet_signs, planet_retrograde, aspects, now, sign, output_dir):
    """Save planetary data to a JSON file for the specified zodiac sign."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        time_utc = now.isoformat() + 'Z'
        focus_planet = ZODIAC_RULERS[sign]
        
        data = {
            "time_utc": time_utc,
            "zodiac_sign": sign,
            "focus_planet": focus_planet,
            "positions": {
                planet: {
                    "x": pos['x'],
                    "y": pos['y'],
                    "z": pos['z'],
                    "zodiac": planet_signs[planet],
                    "retrograde": planet_retrograde[planet]
                } for planet, pos in cartesian_positions.items()
            },
            "aspects": aspects,
            "zodiac_rulers": ZODIAC_RULERS
        }
        
        # Create filename with date, time, and zodiac sign
        date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"planet_positions_{date_time_str}_{sign}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4, cls=NumpyEncoder)
            
        logging.info(f"Saved planet positions for {sign} to {filepath}")
        
    except Exception as e:
        logging.error(f"Error saving planet positions for {sign}: {e}")
        raise

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for handling numpy arrays in JSON."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def create_horoscope_prompt(data):
    """Create a detailed prompt for horoscope generation based on planetary data."""
    try:
        # Build the prompt string using the data from the JSON file
        prompt = f"""You are a master astrologer and research-level analyst trained in both classical and modern astrological traditions. You have been given the exact astronomical positions of all relevant celestial bodies at the moment of birth: this includes the Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, the North and South Nodes, major asteroids (e.g., Ceres, Pallas, Juno, Vesta), and notable fixed stars.

                Your task is to generate a detailed, scholarly natal horoscope analysis that incorporates both the Tropical (Western) and Sidereal (Vedic) zodiac systems, and clearly explains the differences in interpretation between the two frameworks where relevant.

                Include the following:

                A full psychological and karmic profile based on planetary signs, houses, and aspects.

                Clear distinction between Tropical and Sidereal placements when they differ, and commentary on how these affect interpretation.

                An explanation of the precession of the equinoxes and how it informs the Tropical/Sidereal divide.

                Interpretive commentary using both traditional rulerships and modern planetary associations (e.g., Pluto with Scorpio, Uranus with Aquarius).

                Notable configurations (e.g., Grand Cross, Stellium, Yod) and their implications.

                Thematic synthesis of soul lessons, challenges, and life trajectory based on aspects, Nodes, and Chiron.

                Where relevant, mention modern astrological developments such as psychological astrology, evolutionary astrology, or the use of asteroids and fixed stars.

                Use academic-level terminology, integrate cross-tradition insights, and avoid overly generic language.

                Make sure this horoscope reads like a research-level document, integrating both ancient and contemporary astrological thought into a coherent, personalized interpretation.on the following astronomical data:

          """
        for planet, pos in data['positions'].items():
            prompt += f"- {planet}: Coordinates ({pos['x']:.6f}, {pos['y']:.6f}, {pos['z']:.6f}), Zodiac Sign: {pos['zodiac']}, Retrograde: {'Yes' if pos['retrograde'] else 'No'}\n"
            
        prompt += "\nAspects:\n"
        if data['aspects']:
            for aspect in data['aspects']:
                 prompt += f"- {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} at {aspect['angle']} degrees\n"
        else:
            prompt += "None\n"
        
        return prompt
        
    except Exception as e:
        logging.error(f"Error creating horoscope prompt: {e}")
        return str(e)

def generate_horoscope(prompt):
    """Generate a horoscope using the Ollama API based on the provided prompt."""
    try:
        response = ollama.generate(
            model='wizard-vicuna-uncensored:30b',
            prompt=prompt,
            options={
                'temperature': 0.7,
                'max_tokens': 500
            }
        )
        
        if 'results' in response and len(response['results']) > 0:
            return response['results'][0]['message']['content']
            
        return "No valid response generated"
        
    except Exception as e:
        logging.error(f"Error generating horoscope: {str(e)}")
        # Added more detailed error message
        logging.error(f"Full API response: {response}")
        return f"Failed to generate horoscope: {str(e)}"

def main():
    """Main execution function."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Clear output directories
        clear_folder(INPUT_DIR)
        clear_folder(OUTPUT_DIR)
        
        # Calculate planetary positions
        now = datetime.datetime.now()
        cartesian_positions, planet_signs, planet_retrograde, aspects = get_planet_positions(now)
        
        # Generate data for each zodiac sign
        for sign in ZODIAC_SIGNS:
            save_planet_positions(
                cartesian_positions,
                planet_signs,
                planet_retrograde,
                aspects,
                now,
                sign,
                INPUT_DIR
            )
            
        # Process each JSON file to generate horoscopes
        for json_file in os.listdir(INPUT_DIR):
            if json_file.endswith('.json'):
                filepath = os.path.join(INPUT_DIR, json_file)
                
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        
                    # Create the horoscope prompt
                    prompt = create_horoscope_prompt(data)
                    
                    # Generate the horoscope
                    horoscope = generate_horoscope(prompt)
                    print(f"Waiting for Ollama to generate the horoscope for { json_file }...")
                    print(horoscope)
                    
                    # Save the horoscope to the output directory
                    output_filepath = os.path.join(OUTPUT_DIR, f"horoscope_{json_file}")
                    with open(output_filepath, 'w') as f:
                        f.write(horoscope)
                        
                    logging.info(f"Generated horoscope for {data['zodiac_sign']} and saved to {output_filepath}")
                    
                except Exception as e:
                    logging.error(f"Error processing {json_file}: {e}")
                    
    except Exception as e:
        logging.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
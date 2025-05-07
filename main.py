import lmstudio as lms
SERVER_API_HOST = "localhost:1234"
from planets import get_planet_positions as zodata
from planets import get_planets as planet



#calculate planet positions and signs

#agent writes the meaning

#agent writes thje script

#script gets made into audio

#adudio guides the scene animation

#agent uploads it to the socials


data = zodata.get_planet_positions()



def get_planet_positions():



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

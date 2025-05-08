# lumina_project/main_orchestrator.py

import os
import asyncio
import logging
import time
from dotenv import load_dotenv
import psycopg # Or psycopg2 for database interaction
import ollama # Import the ollama library
import time # To potentially manage timing
import requests
# --- Project-Specific Imports (from our defined file structure) ---
# These will be developed in separate files as per the roadmap.
# We'll import them and use placeholder classes/functions for now.
from googleapiclient.discovery import build # For Google API (if needed)
# For AI Brain (Mistral API)
from ai_brain.mistral_api_interface import MistralAPIInterface # Assuming you create this module

# For Data Ingestion (News, Trends)
#from data_ingestion.news_fetcher import NewsFetcher # Assuming you create this module
# from data_ingestion.trend_spotter import TrendSpotter # For later

# For Social Media Posting
#from social_media.post_manager import PostManager # Assuming you create this module
#rom social_media.content_scheduler import ContentScheduler # Assuming you create this module




# --- Configuration ---
# Load environment variables from .env file (for API keys, etc.)
load_dotenv()

# Configuration file paths (relative to this script in the project root)
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
SETTINGS_FILE = os.path.join(CONFIG_DIR, 'settings.yaml') # Placeholder, use if needed
LUMINA_PERSONA_FILE = os.path.join(CONFIG_DIR, 'lumina_persona.txt')

# --- Logging Setup ---
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, 'lumina.log')


# --- Configuration (Get values from environment variables) ---
# Get your Google API Key from your .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Make sure you have GOOGLE_API_KEY in your .env
# Get your Custom Search Engine ID from your .env file
CUSTOM_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ALPHA_ID") # The variable you added


DB_NAME = os.getenv("DB_NAME", "lumina")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434") # Default to localhost if not set
# --- Ollama Embedding Model Configuration ---
OLLAMA_EMBEDDING_MODEL = "all-minilm:l6-v2" # The embedding model pulled in Ollama
# This model outputs 384-dimensional vectors
EMBEDDING_DIMENSION = 384



# --- Database Connection Function ---
def get_db_connection():
    """Establishes and returns a database connection."""
    # Use connection details from environment variables
    if not DB_USER or not DB_PASSWORD or not DB_HOST or not DB_NAME:
         print("Database credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) not fully configured in environment variables.")
         # In a real application, you'd handle this more robustly
         return None
    try:
        # Ensure host is just the address, not address:port for psycopg
        db_host_address = DB_HOST.split(':')[0]
        db_port = DB_HOST.split(':')[1] if ':' in DB_HOST else 5432 # Default port

        conn = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=db_host_address, port=db_port)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# --- Embedding Function using direct requests.post ---
def create_embedding(text):
    """Generates a vector embedding for the given text using Ollama via requests.post."""
    if not OLLAMA_EMBEDDING_MODEL or not OLLAMA_API_BASE_URL:
        print("Ollama configuration (model name or base URL) is missing.")
        return None

    embeddings_url = f"{OLLAMA_API_BASE_URL}/api/embeddings"
    payload = {
        "model": OLLAMA_EMBEDDING_MODEL,
        "prompt": text
    }

    try:
        # Use requests.post to call the embeddings API directly
        response = requests.post(embeddings_url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes

        embedding_result = response.json()

        if 'embedding' in embedding_result:
            embedding = embedding_result['embedding']

            # Optional: Verify dimension here if you want an extra check
            # if len(embedding) != EMBEDDING_DIMENSION:
            #     print(f"Warning: Generated embedding dimension mismatch. Expected {EMBEDDING_DIMENSION}, got {len(embedding)}.")

            return embedding
        else:
            print("Ollama API call successful, but 'embedding' key not found in response.")
            print(f"Response content: {embedding_result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama embeddings API via requests.post: {e}")
        print(f"Please ensure Ollama is running and model '{OLLAMA_EMBEDDING_MODEL}' is pulled and serving embeddings.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during embedding creation: {e}")
        return None


# --- Function to Add Content to the Vector Database ---
def add_memory_to_db(content, source, metadata=None):
    """Adds text content and its embedding to the memories table."""
    conn = get_db_connection()
    if conn is None:
        print("Skipping adding memory due to database connection error.")
        return False

    try:
        embedding = create_embedding(content)
        if embedding is None:
            print("Skipping adding memory due to embedding generation error.")
            if conn: conn.close()
            return False

        # Insert into the memories table
        with conn.cursor() as cur:
            # Ensure your 'memories' table has a 'content' (TEXT),
            # 'embedding' (VECTOR(EMBEDDING_DIMENSION)), 'source' (VARCHAR),
            # and 'timestamp' (TIMESTAMP WITH TIME ZONE) column.
            cur.execute(
                "INSERT INTO memories (content, embedding, source, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
                (content, embedding, source)
            )
            conn.commit()
        print(f"Successfully added memory from source '{source}' to DB.")
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding memory to database: {e}")
        # It's good practice to rollback in case of error
        if conn:
            conn.rollback()
            conn.close()
        return False



# --- Example of how to use this function within your orchestration logic ---
# This would be part of your content generation loop

# Example scenario: Lumina just generated text about a celebrity's birthday and its astrological significance
# llm_generated_text = "Today, we celebrate the cosmic alignment for [Celebrity Name]'s birthday! With [Planetary Aspect], it's a day of [Astrological Meaning]."
# celebrity_name = "A Famous Person"
# astrological_theme = "Mercury in Retrograde"

# --- Craft a query for image search based on the content ---
# You can use keywords from the LLM's output or the input that generated it
# image_query = f"{celebrity_name} {astrological_theme}" # Example query

# --- Perform the image search ---
# relevant_images = search_google_images(image_query, num_results=3) # Get top 3 images

# if relevant_images:
#     print("Found relevant images:", relevant_images)
    # --- Integrate images into the frontend ---
    # Now you would send these image URLs to your JavaScript frontend
    # using the communication method you establish (e.g., WebSocket, Playwright eval).
    # Your JavaScript would update an <img> tag on the HTML stage to display the image.
    # Example (Conceptual command to frontend):
    # send_command_to_frontend({"type": "display_image", "url": relevant_images[0]})
# else:
#     print("Could not find relevant images for the query.")





logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() # Also print to console
    ]
)
logger = logging.getLogger(__name__)



# --- Main Orchestrator Class ---
class LuminaOrchestrator:
    def __init__(self):
        logger.info("Initializing Lumina Orchestrator...")
        self.load_config()

        # Initialize core components (these will be actual class instances later)
        # Ensure the key used here for 'api_key' matches your primary LLM API key in self.settings
        self.mistral_api = MistralAPIInterface(
            api_key=self.settings.get('PRIMARY_LLM_API_KEY'), # Updated to use a generic primary key
            persona_prompt=self.lumina_persona_prompt
        )
        self.news_fetcher = NewsFetcher(
            search_api_key=self.settings.get('CUSTOM_SEARCH_ENGINE_ID '), # Using SEARCHAPI_API_KEY for news
            google_api_key=self.settings.get('GOOGLE_API_KEY') # Alternative for news/search
        )
        self.post_manager = PostManager(
            mistral_api_interface=self.mistral_api,
            x_api_keys=self.settings.get('X_API_KEYS'),
            meta_api_keys=self.settings.get('META_API_KEYS'),
            tiktok_api_keys=self.settings.get('TIKTOK_API_KEYS'),
            reddit_api_keys=self.settings.get('REDDIT_API_KEYS') # Added Reddit
        )
        self.scheduler = ContentScheduler(post_manager=self.post_manager, news_fetcher=self.news_fetcher)
        logger.info("Lumina Orchestrator initialized.")

    def load_config(self):
        """Loads configuration settings and Lumina's persona using provided .env variable names."""
        logger.info("Loading configuration from .env file...")
        
        # Determine primary LLM API key.
        # Prioritize specific keys if available, otherwise use a general one.
        # You mentioned Mistral-small:latest, which might use a specific Mistral key,
        # or be accessed via an OpenAI-compatible endpoint.
        # For this example, let's assume OPENAI_API_KEY is the primary if others aren't specified for Mistral.
        # Please adjust PRIMARY_LLM_API_KEY logic if your Mistral setup uses a different key from your list.
        primary_llm_key = os.getenv("MISTRAL_API_KEY") # Check for a specific Mistral key first
        if not primary_llm_key:
            primary_llm_key = os.getenv("OPENAI_API_KEY") # Fallback or if Mistral uses OpenAI-compatible key
        if not primary_llm_key:
            primary_llm_key = os.getenv("DEEPSEEK_API_KEY") # Another fallback
        # Add more fallbacks if needed, e.g., GOOGLEGEMINI_API_KEY

        self.settings = {
            "PRIMARY_LLM_API_KEY": primary_llm_key,
            "HF_TOKEN": os.getenv("HF_TOKEN"),

            # News/Search APIs
            "SEARCHAPI_API_KEY": os.getenv("SEARCHAPI_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"), # For general Google services, could include news

            # Social Media APIs
            "X_API_KEYS": {
                "api_key": os.getenv("X_API_KEY"),
                "api_key_secret": os.getenv("X_API_KEY_SECRET"),
                "bearer_token": os.getenv("X_BEARER_TOKEN"),
                "access_token": os.getenv("X_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("X_ACCESS_SECRET"), # Note: your list had X_ACCESS_SECRET
            },
            "META_API_KEYS": {
                "app_id": os.getenv("META_APP_ID"),
                "app_secret": os.getenv("META_APP_SECRET"),
                "access_token": os.getenv("META_API_KEY"), # Using your META_API_KEY as the access token
                "app_credentials": os.getenv("META_APP_CREDENTIALS"), # Storing this if needed later
            },
            "TIKTOK_API_KEYS": {
                "client_key": os.getenv("TIKTOK_API_KEY"), # Using your TIKTOK_API_KEY as client_key
                "client_secret": os.getenv("TIKTOK_SECRET_KEY"), # Using your TIKTOK_SECRET_KEY as client_secret
            },
            "REDDIT_API_KEYS": {
                "client_id": os.getenv("REDDIT_CLIENT_ID"),
                "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
                "username": os.getenv("REDDIT_USERNAME"),
                "password": os.getenv("REDDIT_PASSWORD"),
            },

            # Database Configuration (for future use)
            "DB_SETTINGS": {
                "name": os.getenv("DB_NAME"),
                "role": os.getenv("DB_ROLE"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
            },

            # Other API Keys (for future use)
            "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
            "BINANCE_SECRET_KEY": os.getenv("BINANCE_SECRET_KEY"),
            "DEEPSEEK_API_KEY_SECONDARY": os.getenv("DEEPSEEK_API_KEY"), # If used as a secondary/coder
            "OPENAI_API_KEY_SECONDARY": os.getenv("OPENAI_API_KEY"),   # If used as a secondary/coder
            "GOOGLEGEMINI_API_KEY": os.getenv("GOOGLEGEMINI_API_KEY"),
            "HYPERBROWSER_API_KEY": os.getenv("HYPERBROWSER_API_KEY"),
            "GITHUB_API_KEY": os.getenv("GITHUB_API_KEY"),
            
            # Model Choices/Misc
            "MODEL_CRAWL_CHOICE": os.getenv("MODEL_CRAWL_CHOICE"),
        }

        # Validate that essential API keys are present
        if not self.settings["PRIMARY_LLM_API_KEY"]:
            logger.error("PRIMARY_LLM_API_KEY (e.g., MISTRAL_API_KEY, OPENAI_API_KEY) not found in .env file. Exiting.")
            raise ValueError("PRIMARY_LLM_API_KEY is not set. Please ensure your main LLM key is defined in .env.")
        
        # Example validation for X API keys (can be expanded for others)
        if not all(self.settings["X_API_KEYS"].get(k) for k in ["api_key", "api_key_secret", "access_token", "access_token_secret"]):
            logger.warning("One or more X_API_KEYS are missing in .env. X/Twitter functionality may be limited.")


        try:
            with open(LUMINA_PERSONA_FILE, 'r', encoding='utf-8') as f:
                self.lumina_persona_prompt = f.read()
            logger.info("Lumina's persona prompt loaded successfully.")
        except FileNotFoundError:
            logger.error(f"Lumina persona file not found at: {LUMINA_PERSONA_FILE}")
            self.lumina_persona_prompt = "You are Lumina, a friendly AI astrologer."
            logger.warning("Using a default fallback persona.")
        except Exception as e:
            logger.error(f"Error loading Lumina's persona: {e}")
            self.lumina_persona_prompt = "You are Lumina, a friendly AI astrologer."
            logger.warning("Using a default fallback persona due to error.")


    async def run_social_media_cycle(self):
        """
        Main cycle for generating and posting social media content.
        This will be driven by the ContentScheduler.
        """
        logger.info("Starting Lumina's social media content cycle...")
        await self.scheduler.run_pending_tasks() # Example method

    async def start(self):
        """Starts the main loop of the orchestrator."""
        logger.info("Lumina Orchestrator starting...")
        while True:
            try:
                await self.run_social_media_cycle()
                logger.info("Social media cycle complete. Sleeping for 1 hour.") # Adjust as needed
                await asyncio.sleep(3600) 
            except KeyboardInterrupt:
                logger.info("Lumina Orchestrator shutting down due to KeyboardInterrupt.")
                break
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {e}", exc_info=True)
                logger.info("Attempting to recover or sleeping before retrying...")
                await asyncio.sleep(60)

    # --- Future methods for Phase B (Live Streaming) would go here ---
    # async def start_live_stream_components(self):
    #     pass
    # async def handle_live_chat_interaction(self, user_message):
    #     pass

# --- Main Execution Block ---
if __name__ == "__main__":
    # Example usage of the functions
    # Ensure your database is set up and the 'memories' table exists with the correct schema (VECTOR(384))

    print("--- Running Database and Embedding Test ---")

    # The requests tests at the top will run first.

    # Then attempt to add a test memory entry to the database
    print("\nAttempting to add a test memory entry to the database using add_memory_to_db...")
    test_content = "This is a test sentence to confirm database insertion and embedding."
    test_source = "test_insertion"
    success = add_memory_to_db(test_content, test_source)

    if success:
        print("\nTest memory added successfully!")
        print("Please check your 'memories' table in the PostgreSQL database to verify.")
    else:
        print("\nFailed to add test memory using add_memory_to_db. Check console for error messages.")

    # You can add other test calls here if needed
    # get_db_connection() # This will also print connection status

    print("\n--- Test Complete ---")
# orchestrator.py

import os
from dotenv import load_dotenv
# from googleapiclient.discovery import build # Keep if you need Google API services
import psycopg # Or psycopg2 for database interaction
import ollama # Import the ollama library
import time # To potentially manage timing
import requests
# --- Load environment variables ---
load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Keep if needed for Google API services
# CUSTOM_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ALPHA_ID") # Keep if needed
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

# --- Ollama Embedding Model Configuration ---
OLLAMA_EMBEDDING_MODEL = "all-minilm:l6-v2" # The embedding model pulled in Ollama
# This model outputs 384-dimensional vectors
EMBEDDING_DIMENSION = 384


ollama_api_url = "http://localhost:11434" # Replace if your Ollama is on a different address/port

try:
    response = requests.get(ollama_api_url)
    if response.status_code == 200:
        print(f"Successfully connected to Ollama API at {ollama_api_url}.")
        print("Ollama is running and accessible from this Python environment.")
    else:
        print(f"Successfully connected to {ollama_api_url}, but received unexpected status code: {response.status_code}")
        print(f"Response content: {response.text}")
except requests.exceptions.ConnectionError as e:
    print(f"Failed to connect to Ollama API at {ollama_api_url}.")
    print(f"Error details: {e}")
    print("This indicates a network or firewall issue preventing the connection.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


import json

ollama_api_url = "http://localhost:11434/api/embeddings" # Direct embeddings endpoint
embedding_model_name = "all-minilm:l6-v2" # The model you pulled

payload = {
    "model": embedding_model_name,
    "prompt": "This is a test sentence for embedding."
}

try:
    print(f"Attempting to call Ollama embeddings API at {ollama_api_url} for model {embedding_model_name}...")
    response = requests.post(ollama_api_url, json=payload)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    embedding_result = response.json()

    if 'embedding' in embedding_result:
        embedding = embedding_result['embedding']
        print(f"Successfully received embedding from Ollama.")
        print(f"Embedding dimension: {len(embedding)}")
        # print(f"First 10 dimensions: {embedding[:10]}") # Uncomment to see part of the embedding
    else:
        print("Ollama API call successful, but 'embedding' key not found in response.")
        print(f"Full response: {embedding_result}")

except requests.exceptions.ConnectionError as e:
    print(f"Failed to connect to Ollama embeddings API at {ollama_api_url}.")
    print(f"Error details: {e}")
    print("This indicates a network or firewall issue preventing the connection to the specific endpoint.")
except requests.exceptions.RequestException as e:
    print(f"Error calling Ollama embeddings API: Received a non-200 status code.")
    print(f"Error details: {e}")
    print(f"Response content: {e.response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


# --- Database Connection Function ---
def get_db_connection():
    """Establishes and returns a database connection."""
    # Use connection details from environment variables
    if not DB_USER or not DB_PASSWORD or not DB_HOST:
         print("Database credentials or host not fully configured in environment variables.")
         # In a real application, you'd handle this more robustly
         return None
    try:
        conn = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

    print("Database connection established successfully.")

# --- Embedding Function using Ollama ---
def create_embedding(text):
    """Generates a vector embedding for the given text using Ollama."""
    if not OLLAMA_EMBEDDING_MODEL:
        print("Ollama embedding model name is not configured.")
        return None

    try:
        # Call the Ollama embedding API
        # Make sure your Ollama instance is running and the model is pulled
        response = ollama.embeddings(
            model=OLLAMA_EMBEDDING_MODEL,
            prompt=text
        )

        # The embedding vector is in the 'embedding' key of the response
        embedding = response['embedding']

        # Ensure the embedding has the correct dimension
        if len(embedding) != EMBEDDING_DIMENSION:
            print(f"Error: Ollama embedding dimension mismatch for model {OLLAMA_EMBEDDING_MODEL}. Expected {EMBEDDING_DIMENSION}, got {len(embedding)}.")
            # Depending on how you want to handle this, you might raise an error
            return None

        return embedding

    except Exception as e:
        print(f"Error generating embedding with Ollama model {OLLAMA_EMBEDDING_MODEL}: {e}")
        print(f"Please ensure Ollama is running and the model '{OLLAMA_EMBEDDING_MODEL}' is pulled.")
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
            conn.close()
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



if __name__ == "__main__":
    # Example usage of the functions
    # Ensure your database is set up and the 'memories' table exists with the correct schema
    test_content = "This is a test content for embedding."
    test_source = "Test Source"
    add_memory_to_db(test_content, test_source)
    get_db_connection()
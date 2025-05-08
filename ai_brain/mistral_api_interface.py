# ai_brain/mistral_api_interface.py

import os
from openai import OpenAI # We use the standard OpenAI library
from dotenv import load_dotenv # To load environment variables

# Load environment variables from the .env file
load_dotenv()

# --- Configuration ---
# Get the LM Studio API base URL and dummy API key from environment variables
# Make sure these are set in your project's .env file
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1") # Default to common LM Studio address
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio") # Default dummy key

class MistralAPIInterface:
    """
    Handles communication with the LM Studio local API running a Mistral model.
    """
    def __init__(self, model_name):
        """
        Initializes the MistralAPIInterface.

        Args:
            model_name (str): The identifier of the model loaded in LM Studio.
                              E.g., "lmstudio-community/Mistral-Small-3.1-24B-Instruct-2503-GGUF/Mistral-Small-3.1-2403-Q3_K_L.gguf"
        """
        self.model_name = model_name
        # Initialize the OpenAI client, pointing it to the LM Studio server
        self.client = OpenAI(base_url=LM_STUDIO_URL, api_key=LM_STUDIO_API_KEY)
        print(f"Initialized MistralAPIInterface for model: {self.model_name}")
        print(f"API Base URL: {LM_STUDIO_URL}")


    def get_completion(self, messages, temperature=0.7, max_tokens=250, stream=False):
        """
        Sends messages to the LLM and gets a completion response.

        Args:
            messages (list): A list of message dictionaries in the OpenAI format
                             (e.g., [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}])
            temperature (float): Controls randomness (0.0 to 2.0). Lower is more deterministic.
            max_tokens (int): The maximum number of tokens to generate in the response.
            stream (bool): If True, streams the response token by token.

        Returns:
            Union[str, Iterator]: If stream=False, returns the response text (str).
                                 If stream=True, returns an iterator of response chunks.
                                 Returns None if an error occurs.
        """
        try:
            print(f"Sending completion request to model: {self.model_name}")
            # Call the chat completions endpoint
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                # Add other parameters here if needed (e.g., stop sequences, top_p)
            )

            if stream:
                # Return the iterator directly for streaming
                return response
            else:
                # Extract and return the text content for non-streaming
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    print("Received an empty response from the LLM.")
                    return None

        except Exception as e:
            print(f"Error calling LM Studio API: {e}")
            print("Please ensure LM Studio is running and the local server is enabled.")
            return None

# --- Example Usage (for testing this file directly) ---
if __name__ == "__main__":
    # You need LM Studio running with a model loaded and server enabled for this to work

    # Replace with the actual model name loaded in your LM Studio
    # You can find this in the LM Studio Developer tab or when selecting the model in Chat
    TEST_MODEL_NAME = "lmstudio-community/Mistral-Small-3.1-24B-Instruct-2503-GGUF/Mistral-Small-3.1-2403-Q3_K_L.gguf" # Example model name

    # Initialize the interface
    llm_interface = MistralAPIInterface(model_name=TEST_MODEL_NAME)

    # Define a simple test message list
    test_messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Tell me a short, interesting fact about space."}
    ]

    print("\nSending test prompt to LLM...")
    # Get a completion (non-streaming)
    completion = llm_interface.get_completion(test_messages, max_tokens=100)

    if completion:
        print("\nLLM Response:")
        print(completion)
    else:
        print("\nFailed to get LLM response.")

    # Example of streaming (uncomment to test)
    # print("\nSending test prompt to LLM (streaming)...")
    # streaming_completion = llm_interface.get_completion(test_messages, max_tokens=100, stream=True)

    # if streaming_completion:
    #     print("\nLLM Response (streaming):")
    #     for chunk in streaming_completion:
    #         if chunk.choices[0].delta.content is not None:
    #             print(chunk.choices[0].delta.content, end="", flush=True)
    #     print() # Newline at the end
    # else:
    #      print("\nFailed to get streaming LLM response.")


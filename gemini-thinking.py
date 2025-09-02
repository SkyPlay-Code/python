from google import genai
from google.genai import types

# Initialize the client with API key
client = genai.Client(api_key="AIzaSyDZIpa8sya6wPRlNuzh1TJx07-k-rXPDY8")  # Replace with your actual API key

# Basic thinking example with default configuration
def basic_thinking():
    prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=prompt
    )
    print(response.text)

# Advanced thinking with custom thinking budget
def advanced_thinking():
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents="Explain the Occam's Razor concept and provide everyday examples of it",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024)
        ),
    )
    print(response.text)

# Example usage - uncomment the function you want to test
if __name__ == "__main__":
    # basic_thinking()
    # advanced_thinking()
    pass
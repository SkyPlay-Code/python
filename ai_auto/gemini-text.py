from google import genai
from google.genai import types
from PIL import Image

# Initialize the client with API key
client = genai.Client(api_key="GEMINI_API_KEY")  # Replace with your actual API key

# Basic text generation
def basic_text_generation():
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["How does AI work?"]
    )
    print(response.text)

# Image analysis with text prompt
def image_analysis():
    image = Image.open("Screenshot 2025-05-05 115555.png")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[image, "What are you seeing in this image?"]
    )
    print(response.text)

# Streaming text generation
def streaming_text_generation():
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=["Explain how AI works"]
    )
    for chunk in response:
        print(chunk.text, end="")

# Chat conversation with history
def chat_conversation():
    chat = client.chats.create(model="gemini-2.0-flash")
    
    # Send messages
    response = chat.send_message("I have 2 dogs in my house.")
    print(response.text)
    
    response = chat.send_message("How many paws are in my house?")
    print(response.text)
    
    # Print chat history
    for message in chat.get_history():
        print(f'role - {message.role}', end=": ")
        print(message.parts[0].text)

# Streaming chat conversation
def streaming_chat():
    chat = client.chats.create(model="gemini-2.0-flash")
    
    # Stream first message
    response = chat.send_message_stream("I have 2 dogs in my house.")
    for chunk in response:
        print(chunk.text, end="")
    
    # Stream second message
    response = chat.send_message_stream("How many paws are in my house?")
    for chunk in response:
        print(chunk.text, end="")
    
    # Print chat history
    for message in chat.get_history():
        print(f'role - {message.role}', end=": ")
        print(message.parts[0].text)

# Text generation with custom configuration
def custom_config_generation():
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["Explain how AI works"],
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            temperature=0.1
        )
    )
    print(response.text)

# System instruction example (role-playing as a cat)
def system_instruction_example():
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a cat. Your name is Neko."),
        contents="Hello there"
    )
    print(response.text)

# Example usage - uncomment the function you want to test
if __name__ == "__main__":
    basic_text_generation()
    # image_analysis()
    # streaming_text_generation()
    # chat_conversation()
    # streaming_chat()
    # custom_config_generation()
    # system_instruction_example()
    pass
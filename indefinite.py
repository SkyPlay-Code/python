# To run this code you need to install the following dependencies:
# pip install google-genai

import time
import re
import os
import google.generativeai as genai

def sanitize_filename(name):
    """
    Takes a string and returns a safe filename for any OS.
    Removes illegal characters, replaces spaces, and limits length.
    """
    # Remove the .py extension if the model includes it
    if name.lower().endswith('.py'):
        name = name[:-3]
    # Replace spaces and hyphens with a single underscore
    name = re.sub(r'[\s-]+', '_', name)
    # Remove any characters that are not letters, numbers, or underscores
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    # Ensure the filename is not empty after sanitization
    if not name:
        return "unnamed_script"
    return name

def generate_and_save_code():
    """
    Continuously generates Python code, derives a filename from it,
    and saves each script to a separate .txt file.
    Uses a hardcoded API key for testing purposes.
    """
    # --- IMPORTANT ---
    # Replace the key below with your actual Google Gemini API key.
    # Warning: Hardcoding keys is a security risk. Do not share this file
    # publicly or commit it to version control with your key inside.
    API_KEY = "AIzaSyBxewcKiere8qDUtVGejHyJ_aDprxuaMaM" # This is a hardcoded test key as requested

    try:
        if API_KEY == "YOUR_API_KEY_HERE" or len(API_KEY) < 30:
            print("Error: Please replace the placeholder with your actual Gemini API key.")
            return

        genai.configure(api_key=API_KEY)

        # Using a modern and capable model.
        model = genai.GenerativeModel('gemini-2.5-pro')

        # The chat history now instructs the model to provide a filename in a specific format.
        chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": ["""
You are an expert Python code generator. Your task is to generate a different, random, and meaningful Python script each time I ask.

IMPORTANT: You must follow this format for every response:
1. On the very first line, provide a short, descriptive filename for the script (e.g., `password_generator.py` or `simple_web_server.py`).
2. On the second line, type exactly three hyphens: `---`.
3. Starting from the third line, provide the complete, runnable Python code.

Example Response:
file_renamer.py
---
import os

def rename_files_in_directory(directory, prefix):
    # ... rest of the code ...
"""]
            },
            {
                "role": "model",
                "parts": ["Understood. I will provide a descriptive filename, followed by `---`, and then the complete Python script in every response."]
            }
        ])

        print("--- Starting Random Code Generation and Saving ---")
        print("Press Ctrl+C to stop the script.")

        while True:
            print("\n" + "="*50)
            print("⏳ Generating new Python script...")

            # We send the request and get the full response at once to parse it.
            response = chat.send_message("Generate the next Python script and its corresponding filename.")
            
            full_response_text = response.text
            
            # Parsing logic to separate filename and code based on the '---' separator
            if '---' in full_response_text:
                parts = full_response_text.split('---', 1)
                
                filename_suggestion = parts[0].strip()
                python_code = parts[1].strip()

                # Check if the model returned valid parts
                if not filename_suggestion or not python_code:
                    print("❌ Error: Model returned an empty filename or code. Skipping this generation.")
                    time.sleep(5)
                    continue

                # Sanitize the filename and add the .txt extension
                safe_base_name = sanitize_filename(filename_suggestion)
                output_filename = f"{safe_base_name}.txt"

                print(f"✅ Generation complete. Suggested filename: '{filename_suggestion}'")

                # Save the code to the new text file
                try:
                    with open(output_filename, "w", encoding="utf-8") as f:
                        f.write(python_code)
                    print(f"💾 Successfully saved code to '{output_filename}'")
                except IOError as e:
                    print(f"❌ Error saving file: {e}")

            else:
                print("❌ Error: The model's response did not follow the required format (missing '---').")
                print("--- Full Model Response ---")
                print(full_response_text)
                print("---------------------------")

            # A delay to avoid hitting API rate limits too quickly.
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\nScript stopped by user. Exiting.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("This might be due to an invalid API key, network issues, or API rate limits.")

if __name__ == "__main__":
    generate_and_save_code()
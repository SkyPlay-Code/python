import os
import google.generativeai as genai

# BIG BOLD WARNING: This script executes code returned directly from an AI.
# This is a REAL security risk. An AI can be tricked into generating malicious
# code (e.g., 'os.system("rm -rf /")'). 
# DO NOT RUN THIS IN A PRODUCTION ENVIRONMENT. Use it for learning and fun only.

# --- Step 1: Configure the Gemini Client ---
TEMP_API_KEY = "GEMINI_API_KEY" 
genai.configure(api_key=TEMP_API_KEY)

def ask_ai_for_code(prompt: str) -> str:
    """
    Makes a live API call to Google Gemini to generate Python code.
    """
    print(f"\n[AI Request] Sending prompt to Gemini: '{prompt}'")
    
    # --- Step 2: Craft a very specific prompt for the AI ---
    # We instruct it to only return raw code to make parsing easy and reliable.
    # This is a key part of the "hack".
    system_instruction = (
        "You are a Python code generator. Your sole purpose is to write a single, "
        "self-contained Python function named 'dynamic_function' that accomplishes the user's goal. "
        "Do NOT include any markdown (like ```python), explanations, or any text other than the Python code itself."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro', # Using the faster model is good for this use case
        system_instruction=system_instruction
    )
    
    try:
        response = model.generate_content(prompt)
        # The raw code is in the 'text' part of the response
        code_string = response.text
        print(f"[AI Response] Received code block:\n---\n{code_string}\n---")
        return code_string.strip()
    except Exception as e:
        print(f"[AI Error] Failed to get response from Gemini API: {e}")
        # Return a safe error function if the API call fails
        return "def dynamic_function(*args, **kwargs):\n    print('AI API call failed.')"


def execute_ai_code(prompt: str, *args):
    """
    Gets code from the Gemini AI and executes it in a controlled scope.
    """
    # 1. Get the code from the live AI
    code_string = ask_ai_for_code(prompt)
    
    # 2. This is the dangerous part: execute the string as Python code.
    # We create a local scope (dictionary) for the exec to run in.
    local_scope = {}
    
    print("[Execution] Attempting to execute AI-generated code...")
    try:
        exec(code_string, {}, local_scope)
        
        # 3. Retrieve the function we just created from the string
        function_to_run = local_scope.get('dynamic_function')
        
        if function_to_run:
            # 4. Run the dynamically created function
            result = function_to_run(*args)
            print(f"--> AI Code Result: {result}")
        else:
            print("[Execution Error] 'dynamic_function' not found in AI response.")

    except Exception as e:
        print(f"[Execution Error] An error occurred while running AI code: {e}")


# --- Let's run it live! ---

# Example 1: A simple math problem
execute_ai_code("A funtion that calculates the volume and area of all kind of 3d and 2d shapes by taking input from user, if the user enters none or no value then some random value will be taken everytime instead of fixed value.")
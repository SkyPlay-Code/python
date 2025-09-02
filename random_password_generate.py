import random
import string

def generate_password(length):
  """Generates a random password of a specified length."""
  # Define the character sets to use: lowercase, uppercase, digits, and punctuation
  characters = string.ascii_letters + string.digits + string.punctuation

  # Validate the password length
  if length < 1:
    return "Error: Password length must be at least 1."

  # Generate the password by randomly choosing characters from the defined set
  # random.choice(characters) selects a random character from the 'characters' string
  # the loop runs 'length' times to build the password string
  # ''.join(...) concatenates the chosen characters into a single string
  password = ''.join(random.choice(characters) for _ in range(length))

  return password

# --- How to run this script ---
# Save this code as a Python file (e.g., generate_password.py).
# Open a terminal or command prompt.
# Navigate to the directory where you saved the file.
# Run the script using the command: python generate_password.py
# The script will then prompt you to enter the desired password length.
# -----------------------------

# Get the desired password length from the user via command line input
# This part will only work when you run the script in your local environment
while True:
  try:
    # Prompt the user to enter the password length
    password_length_str = input("Enter the desired password length: ")
    # Convert the input string to an integer
    password_length = int(password_length_str)
    # Break the loop if the input is a valid integer
    break
  except ValueError:
    # Handle cases where the input is not a valid integer
    print("Invalid input. Please enter an integer for the password length.")
  except EOFError:
      # Handle potential EOFError in some environments, though less common for simple input()
      print("\nInput stream closed. Exiting.")
      exit()


# Generate the password using the user-provided length
random_password = generate_password(password_length)

# Print the generated password
print("Generated Password:", random_password)

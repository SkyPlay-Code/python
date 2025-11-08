import random

def get_computer_choice():
  """Randomly selects Rock, Paper, or Scissors for the computer."""
  choices = ["rock", "paper", "scissors"]
  return random.choice(choices)

def get_user_choice():
  """Gets and validates the user's choice."""
  while True:
    user_input = input("Enter your choice (rock, paper, or scissors): ").lower()
    if user_input in ["rock", "paper", "scissors"]:
      return user_input
    else:
      print("Invalid choice. Please enter 'rock', 'paper', or 'scissors'.")

def determine_winner(user_choice, computer_choice):
  """Determines the winner of the round."""
  if user_choice == computer_choice:
    return "tie"
  elif (user_choice == "rock" and computer_choice == "scissors") or \
       (user_choice == "paper" and computer_choice == "rock") or \
       (user_choice == "scissors" and computer_choice == "paper"):
    return "win"
  else:
    return "lose"

def play_game():
  """Runs the main game loop."""
  print("Welcome to Rock Paper Scissors!")

  while True:
    user_choice = get_user_choice()
    computer_choice = get_computer_choice()

    print(f"\nYou chose: {user_choice}")
    print(f"Computer chose: {computer_choice}")

    result = determine_winner(user_choice, computer_choice)

    if result == "tie":
      print("It's a tie!")
    elif result == "win":
      print("You win!")
    else:
      print("You lose!")

    # Ask if the user wants to play again
    while True:
      play_again = input("Play again? (yes/no): ").lower()
      if play_again in ["yes", "no"]:
        break
      else:
        print("Invalid input. Please enter 'yes' or 'no'.")

    if play_again == "no":
      break

  print("\nThanks for playing!")

# --- How to run this script ---
# Save this code as a Python file (e.g., rps_game.py).
# Open a terminal or command prompt.
# Navigate to the directory where you saved the file.
# Run the script using the command: python rps_game.py
# The game will then start in your terminal.
# -----------------------------

# Start the game when the script is executed
if __name__ == "__main__":
  play_game()

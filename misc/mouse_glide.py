import pyautogui
import random
import time

# Set a fail-safe to stop the script by moving the mouse to a corner
pyautogui.FAILSAFE = True

print("Press Ctrl+C to quit.")

try:
    while True:
        # Get the screen dimensions
        screenWidth, screenHeight = pyautogui.size()

        # Generate random coordinates to move to
        x = random.randint(0, screenWidth - 1)
        y = random.randint(0, screenHeight - 1)

        # Generate a random duration for the mouse movement
        move_duration = random.uniform(0.5, 2.5) # Glides for 0.5 to 2.5 seconds

        # Move the mouse in a human-like way
        pyautogui.moveTo(x, y, duration=move_duration, tween=pyautogui.easeOutQuad)
        print(f"Moved to ({x}, {y}) over {move_duration:.2f} seconds.")

        # This is a key part: perform a small scroll action.
        # This is often more effective than just movement. A value of 1 or -1 is very subtle.
        scroll_amount = random.choice([1, -1])
        pyautogui.scroll(scroll_amount)
        print(f"Scrolled by {scroll_amount} unit.")


        # Wait for a random interval before the next movement
        sleep_interval = random.randint(15, 45) # Waits between 15 and 45 seconds
        print(f"Sleeping for {sleep_interval} seconds.")
        time.sleep(sleep_interval)

except KeyboardInterrupt:
    print('\nScript terminated by user.')
except pyautogui.FailSafeException:
    print('\nFail-safe triggered! Script terminated.')
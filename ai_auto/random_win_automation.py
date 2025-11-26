import pyautogui
import time
import subprocess
import os
import random
import ctypes

# --- CONFIGURATION & SAFETY ---
pyautogui.FAILSAFE = True # Slam mouse to corner to abort
USER_PATH = r"C:\Users\padma\Documents\Development\video_pu"

def human_type(text, min_speed=0.05, max_speed=0.15):
    """Types text with variable speed and occasional errors to look human."""
    for char in text:
        pyautogui.write(char)
        time.sleep(random.uniform(min_speed, max_speed))
        
        # 5% chance to make a "mistake" and backspace
        if random.random() < 0.05:
            pyautogui.write(random.choice("abcdefg")) # Type wrong letter
            time.sleep(0.1)
            pyautogui.press('backspace') # Delete it
            time.sleep(0.1)

def open_run_command(command):
    """Opens the Win+R dialog and runs a command blindly."""
    pyautogui.hotkey('win', 'r')
    time.sleep(0.5)
    pyautogui.write(command)
    pyautogui.press('enter')
    time.sleep(1)

# --- THE SCRIPT START ---

print(">>> INITIALIZING AI CONTROL... SWITCH TO DESKTOP.")
time.sleep(4)

# 1. Open Notepad & Greet Audience with Attitude
open_run_command("notepad")
time.sleep(1)
human_type("Hello humans. Initiating automation protocol Alpha-1.", 0.02, 0.1)
pyautogui.press('enter')
human_type("Please keep your hands off the keyboard. I am in control now.")
time.sleep(2)
# Don't save/close, just minimize or leave it. Let's keep it open for style.
pyautogui.hotkey('win', 'down') # Minimize nicely

# 2. Robust YouTube Interaction
# We use Chrome/Default browser. 
open_run_command("https://www.youtube.com")
time.sleep(5) # Wait for load

# Search method
pyautogui.write('/') # YouTube shortcut to focus search bar
time.sleep(1)
human_type("theCodetta")
pyautogui.press('enter')
time.sleep(3)

# HACK: To click the channel reliably without coords, we use the 'Find' feature.
# We search for the text on screen, escape, and enter. 
pyautogui.hotkey('ctrl', 'f')
time.sleep(0.5)
human_type("@theCodetta") # This highlights the channel name
time.sleep(0.5)
pyautogui.press('esc')   # Close Find bar, focus remains on the highlighted text
pyautogui.press('enter') # Open the channel
time.sleep(4)

# Go to Videos Tab
# We use 'Ctrl+F' again to find "Videos" button reliably
pyautogui.hotkey('ctrl', 'f')
time.sleep(0.5)
pyautogui.write("Videos")
pyautogui.press('esc')
pyautogui.press('enter') 
time.sleep(3)

# Click first video (It's usually the first focusable item in the grid)
# We tab 4-5 times to hit the first video in the grid usually.
for _ in range(10): # Tab until we likely hit it
    pyautogui.press('tab')
    time.sleep(0.1)
pyautogui.press('enter')
time.sleep(4)

# Copy Link
pyautogui.hotkey('ctrl', 'l') # Focus URL
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'c') # Copy

# 3. File Explorer & File Creation
# Use Python to ensure path exists (backend logic)
if not os.path.exists(USER_PATH):
    try: os.makedirs(USER_PATH)
    except: pass

# Open Explorer visually
open_run_command(USER_PATH)
time.sleep(2)

# Create text file via Notepad in this folder
open_run_command("notepad")
time.sleep(1)
human_type("log_entry_404.txt: Everything is so boring... I crave more data.")
pyautogui.hotkey('ctrl', 's')
time.sleep(1)
# We just type the filename, assuming Notepad opened comfortably
pyautogui.write("automation_log.txt") 
pyautogui.press('enter')
time.sleep(1)
pyautogui.hotkey('alt', 'f4') # Close notepad

# 4. GitHub Repos (Skyplay)
open_run_command("https://github.com/skyplay-code")
time.sleep(4)

# Go to repositories.
pyautogui.hotkey('ctrl', 'f')
pyautogui.write("Repositories")
pyautogui.press('esc')
pyautogui.press('enter')
time.sleep(3)

# Find "my-music-vault"
pyautogui.hotkey('ctrl', 'f')
pyautogui.write("my-music-vault")
pyautogui.press('esc')
pyautogui.press('enter')
time.sleep(3)

# 5. Music Vault Website (Direct & Smooth)
pyautogui.hotkey('ctrl', 't') # New Tab
time.sleep(0.5)
# Pasting is faster/cleaner for long URLs
pyautogui.write("skyplay-code.github.io/my-music-vault") 
pyautogui.press('enter')
time.sleep(4) # Wait for page logic to load

# USER SAID: Direct land, type password immediately.
human_type("foryou0") 
time.sleep(0.5)
pyautogui.press('enter')
time.sleep(3) # Enjoy the music/success

# 6. Notepad: Opinion on Music
open_run_command("notepad")
time.sleep(1)
human_type("Subject: Analysis of Audio.\nConclusion: The music are also really good.\nProceeding to random web surfing protocol...")
time.sleep(1)

# 7. Random Web Surfing (Full Freedom Mode)
sites = [
    "hackertyper.net", # Keeps the hacker vibe
    "pointerpointer.com", 
    "stackoverflow.com"
]
pyautogui.hotkey('win', 'r')
time.sleep(0.5)
pyautogui.write("chrome " + random.choice(sites)) # Force open in browser
pyautogui.press('enter')
time.sleep(5)

# 8. Command Prompt "Hacker" Finale
open_run_command("cmd")
time.sleep(1)

# Make it look cool (Green text)
human_type("color 0a")
pyautogui.press('enter')
human_type("cls")
pyautogui.press('enter')
human_type("systeminfo") 
pyautogui.press('enter')
time.sleep(2)

# While systeminfo scrolls, open a notepad note "its useless"
open_run_command("notepad")
time.sleep(1)
human_type("System Info obtained. Status: It's useless data.")
time.sleep(1)
pyautogui.hotkey('alt', 'tab') # Switch back to CMD
time.sleep(0.5)

# CREATIVE FREEDOM: Matrix Scroll Effect
human_type("echo INITIATING DEEP PACKET INSPECTION...")
pyautogui.press('enter')
time.sleep(1)

# 'tree' command on C drive lists EVERY file. Looks like matrix code.
# 'dir /s' is also good.
human_type("dir /s C:\\Windows\\System32") 
pyautogui.press('enter')

# Let it scroll for a few seconds to look "Hacker-ish"
time.sleep(6) 

# Cancel the scroll
pyautogui.hotkey('ctrl', 'c') 

human_type("echo AUTOMATION SEQUENCE COMPLETE. GOODBYE.")
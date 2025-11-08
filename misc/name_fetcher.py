import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

def get_document_titles():
    """
    Reads a list of Google Drive URLs from a file, visits each one using Selenium,
    extracts the document title, and saves the results to a new file.
    """
    input_filename = "iit_jee_drive_links.txt"
    output_filename = "named_drive_links.txt"

    # --- 1. Read the list of URLs from the input file ---
    try:
        with open(input_filename, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
        if not links:
            print(f"[ERROR] The input file '{input_filename}' is empty. Please run the first script again.")
            return
        print(f"[INFO] Found {len(links)} links to process from '{input_filename}'.")
    except FileNotFoundError:
        print(f"[ERROR] The input file '{input_filename}' was not found.")
        print("Please make sure it is in the same folder as this script.")
        return

    # --- 2. Set up the Selenium WebDriver ---
    print("[INFO] Setting up browser driver...")
    try:
        options = webdriver.ChromeOptions()
        # The next line makes the browser window run in the background (headless)
        # Remove the line if you want to watch the browser work.
        options.add_argument('--headless')
        options.add_argument('--log-level=3') # Suppress unnecessary console logs
        options.add_argument('--disable-gpu') # Often needed for headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"[ERROR] Could not start the browser. Please ensure Google Chrome is installed. Error: {e}")
        return
        
    named_links = []

    # --- 3. Loop through each link, get the title, and store it ---
    print("[INFO] Starting to process links. A browser is running in the background...")
    for i, link in enumerate(links):
        print(f"  -> Processing link {i+1} of {len(links)}...")
        try:
            driver.get(link)
            # Wait for the page's title to load. 4 seconds is usually safe.
            time.sleep(4) 
            
            title = driver.title
            
            # Clean up the title from the standard Google Drive suffix
            if " - Google Drive" in title:
                title = title.replace(" - Google Drive", "").strip()
            
            if not title or "Google Drive" in title:
                title = "Unknown_Title" # Fallback for failed loads
                print(f"     [WARN] Could not get a proper title for {link}. Marking as Unknown.")

            # Store the formatted result
            named_links.append(f"{title}: {link}")

        except WebDriverException as e:
            print(f"     [ERROR] Failed to process the link {link}. Error: {e}")
            named_links.append(f"FAILED_TO_LOAD: {link}")

    # --- 4. Close the browser ---
    driver.quit()

    # --- 5. Write the results to the output file ---
    with open(output_filename, 'w', encoding='utf-8') as f:
        for item in named_links:
            f.write(item + '\n')
            
    print("\n--------------------------------------------------")
    print("Process complete!")
    print(f"All titles have been saved to '{output_filename}'")
    print("--------------------------------------------------")

if __name__ == "__main__":
    get_document_titles()
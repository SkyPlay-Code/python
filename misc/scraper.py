import requests
from bs4 import BeautifulSoup
import time

def get_soup(url):
    """Fetches the content from a URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    """Main function to scrape all IIT-JEE Google Drive links from iitianacademy.com."""
    
    # List of the main pages containing chapter-wise study materials
    base_urls = [
        "https://www.iitianacademy.com/iit-jee-main-physics-study-materials-chapter-wise/",
        "https://www.iitianacademy.com/iit-jee-main-chemistry-study-materials-chapter-wise-2/",
        "https://www.iitianacademy.com/iit-jee-main-maths-study-materials-chapter-wise-2/",
        "https://www.iitianacademy.com/iit-jee-advanced-physics-study-materials-chapterwise/",
        "https://www.iitianacademy.com/iit-jee-advanced-chemistry-study-materials-chapter-wise/",
        "https://www.iitianacademy.com/iit-jee-advanced-maths-study-materials-chapter-wise/"
    ]

    all_drive_links = set()

    print("Starting the scraping process...")

    # Loop through each main subject/level page
    for url in base_urls:
        print(f"\n[INFO] Scraping category: {url}")
        soup = get_soup(url)
        if not soup:
            continue

        # Find the main content area where chapter links are listed
        # Inspected from the website's source, links are within <div class="entry-content">
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            print(f"  [WARN] Could not find content area in {url}")
            continue

        chapter_links = [a['href'] for a in content_div.find_all('a', href=True)]
        print(f"  [INFO] Found {len(chapter_links)} chapter links.")

        # Loop through each chapter page to find the drive links
        for chapter_url in chapter_links:
            print(f"    -> Visiting chapter: {chapter_url}")
            chapter_soup = get_soup(chapter_url)
            if not chapter_soup:
                continue

            # Find all links that point to Google Drive
            drive_links_on_page = [
                a['href'] for a in chapter_soup.find_all('a', href=True) 
                if 'drive.google.com' in a['href']
            ]
            
            for link in drive_links_on_page:
                print(f"      [SUCCESS] Found Google Drive link: {link}")
                all_drive_links.add(link)

            # Be polite to the server by waiting a second between requests
            time.sleep(1)

    # Save all unique links to a file
    output_filename = "iit_jee_drive_links.txt"
    with open(output_filename, 'w') as f:
        for link in sorted(list(all_drive_links)):
            f.write(link + '\n')

    print(f"\n--------------------------------------------------")
    print(f"Process complete!")
    print(f"Found a total of {len(all_drive_links)} unique Google Drive links.")
    print(f"All links have been saved to '{output_filename}'")
    print(f"--------------------------------------------------")

if __name__ == "__main__":
    main()
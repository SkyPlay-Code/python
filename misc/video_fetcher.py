# Check for dependencies first and guide the user.
try:
    import os
    import sys
    import yt_dlp
    from seleniumwire import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from yt_dlp.utils import DownloadError

except ImportError as e:
    missing_module = e.name
    print(f"\n[-] ERROR: Prerequisite module '{missing_module}' is not installed.")
    
    # Provide specific installation instructions
    if missing_module == 'yt_dlp':
        print("[*] To fix this, run: pip install yt_dlp")
    elif missing_module == 'seleniumwire':
        print("[*] This module requires a specific version of 'blinker'.")
        print("[*] To fix this, run: pip install selenium-wire \"blinker==1.4\"")
    elif missing_module == 'webdriver_manager':
        print("[*] To fix this, run: pip install webdriver-manager")
    else:
        print(f"[*] Please install '{missing_module}' using pip.")
        
    sys.exit("\n[!] Aborting. Please install the required modules and re-run the script.")

# --- ASCII Art Banner ---
def display_banner():
    print(r"""
    ██╗   ██╗██╗██████╗ ███████╗ ██████╗        ██████╗  ██████╗ ██████╗  ██████╗ ██████╗  ██████╗ ██╗     
    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗       ██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝ ██║     
    ██║   ██║██║██║  ██║█████╗  ██║   ██║█████╗ ██████╔╝██║   ██║██████╔╝██║   ██║██████╔╝██║      ██║     
    ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║╚════╝ ██╔══██╗██║   ██║██╔══██╗██║   ██║██╔══██╗██║      ██║     
     ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝       ██║  ██║╚██████╔╝██████╔╝╚██████╔╝██║  ██║╚██████╗ ███████╗
      ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝        ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                            >> Video Acquisition Protocol v2.0 <<
    """)

def direct_download(video_url, save_path='.'):
    """
    Attempts a direct payload extraction using yt-dlp.
    """
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,  # Suppress yt-dlp's default logging
        'progress_hooks': [lambda d: print(f"[*] Status: {d['_percent_str']} done...", end='\r') if d['status'] == 'downloading' else None],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"[*] Initializing direct connection for: {video_url}")
        ydl.download([video_url])
        sys.stdout.write("\n") # New line after progress bar finishes
        print(f"[+] Direct download successful. File saved in: {save_path}")

def intercept_and_download(page_url, save_path='.'):
    """
    Engages network interception to uncover and download protected video streams.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # Suppress verbose browser logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Set up Selenium Service to send chromedriver logs to null
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)
    
    print("[*] Initializing stealth browser for network analysis...")
    driver = webdriver.Chrome(service=service, options=options)
    
    m3u8_url = None
    request_headers = None
    
    try:
        driver.get(page_url)
        print(f"[*] Target page loaded. Now sniffing network traffic for .m3u8 manifest...")
        
        request = driver.wait_for_request(r'\.m3u8', timeout=25)
        m3u8_url = request.url
        request_headers = request.headers
        print(f"[+] Manifest intercepted: {m3u8_url}")

    except Exception:
        print(f"[-] Interception failed. No .m3u8 manifest detected within the timeout period.")
        return
    finally:
        driver.quit()

    if m3u8_url:
        print("\n[*] Passing intercepted stream to the download module...")
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'format': 'best',
            'http_headers': request_headers,
            'merge_output_format': 'mp4',
            'quiet': True,
            'progress_hooks': [lambda d: print(f"[*] Status: {d['_percent_str']} done...", end='\r') if d['status'] == 'downloading' else None],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([m3u8_url])
                sys.stdout.write("\n")
                print(f"[+] Download complete! File acquired in '{save_path}'")
        except Exception as e:
            print(f"\n[-] An error occurred during the final download phase: {e}")

if __name__ == '__main__':
    display_banner()
    video_link = input("   Enter Target URL >> ")
    output_directory = input("   Enter Save Directory (or press Enter for current) >> ") or '.'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"[+] Created directory: {output_directory}")

    try:
        print("\n[+]--- Starting Protocol 1: Direct Acquisition ---[+]")
        direct_download(video_link, output_directory)
        
    except DownloadError:
        print("\n[-] Direct acquisition failed. The target may be using anti-download measures.")
        print("[+]--- Initiating Protocol 2: Network Interception ---[+]")
        
        try:
            intercept_and_download(video_link, output_directory)
        except Exception as intercept_e:
            print(f"\n[-] Network Interception Protocol failed: {intercept_e}")
            print("[!] Both acquisition methods have failed. Mission aborted.")
            
    except Exception as e:
        print(f"\n[-] An unexpected system error occurred: {e}")
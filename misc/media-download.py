import yt_dlp
import os

# URL of a public domain video (e.g., from the Internet Archive or NASA)
# This is "A Trip to the Moon" (1902), which is in the public domain.
video_url = 'https://youtu.be/F4rKeQ8_NlQ?si=dxAmNU2dyZE-yb-1'

# --- Example 1: Download the best quality video and audio combined ---

def download_best_video(url, output_path='downloads'):
    """
    Downloads the best quality video available.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Set the options for yt-dlp
    # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    # This tries to get the best MP4 video and M4A audio and merge them.
    # If that's not possible, it falls back to the best pre-merged MP4, then any best format.
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'), # Saves file as 'Video Title.mp4'
        'noplaylist': True, # Only download a single video, not a whole playlist
    }

    print(f"Downloading video from: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Video download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Example 2: Download audio only as an MP3 file ---

def download_audio_only(url, output_path='downloads/audio'):
    """
    Downloads only the audio and converts it to MP3.
    Requires FFmpeg to be installed.
    """
    os.makedirs(output_path, exist_ok=True)
    
    # Set the options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # 192 kbps quality
        }],
    }

    print(f"Downloading audio from: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Audio extraction completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


# --- Run the functions ---
if __name__ == "__main__":
    print("Choose an option:")
    print("1: Download best quality video")
    print("2: Download audio only (MP3)")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        download_best_video(video_url)
    elif choice == '2':
        download_audio_only(video_url)
    else:
        print("Invalid choice.")
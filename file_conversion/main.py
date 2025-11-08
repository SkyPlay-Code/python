import os
import sys

# Import the 'rich' library components
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Import the newly created main function from each of our converter scripts
# (Make sure to apply the refactoring change to all of them first!)
from audio_conversion import main as main_audio
from video_conversion import main as main_video
from image_conversion import main as main_image
from document_conversion import main as main_document
from archive_conversion import main as main_archive
from powerpoint_conversion import main as main_presentation
from font_conversion import main as main_font
from ebook_conversion import main as main_ebook

# Create a console object
console = Console()

# --- The core of the auto-detection logic ---
# A mapping of file extensions to their corresponding conversion type and function
FILE_TYPE_MAPPING = {
    # Audio Formats
    ".mp3": ("Audio", main_audio), ".wav": ("Audio", main_audio), ".flac": ("Audio", main_audio),
    ".aac": ("Audio", main_audio), ".ogg": ("Audio", main_audio), ".wma": ("Audio", main_audio),
    ".m4a": ("Audio", main_audio), ".aiff": ("Audio", main_audio),

    # Video Formats
    ".mp4": ("Video", main_video), ".mkv": ("Video", main_video), ".mov": ("Video", main_video),
    ".avi": ("Video", main_video), ".wmv": ("Video", main_video), ".flv": ("Video", main_video),
    ".webm": ("Video", main_video),

    # Image Formats
    ".png": ("Image", main_image), ".jpg": ("Image", main_image), ".jpeg": ("Image", main_image),
    ".gif": ("Image", main_image), ".bmp": ("Image", main_image), ".tiff": ("Image", main_image),
    ".webp": ("Image", main_image), ".heic": ("Image", main_image), ".psd": ("Image", main_image),
    ".cr2": ("Image", main_image), ".nef": ("Image", main_image), ".arw": ("Image", main_image),

    # Document Formats
    ".docx": ("Document", main_document), ".doc": ("Document", main_document),
    ".odt": ("Document", main_document), ".rtf": ("Document", main_document),
    ".txt": ("Document", main_document), ".html": ("Document", main_document), ".htm": ("Document", main_document),
    ".pdf": ("Document", main_document), ".xps": ("Document", main_document), # PDF is special-cased as a document first

    # Presentation Formats
    ".pptx": ("Presentation", main_presentation), ".ppt": ("Presentation", main_presentation),
    ".odp": ("Presentation", main_presentation),

    # Archive Formats
    ".zip": ("Archive", main_archive), ".rar": ("Archive", main_archive), ".7z": ("Archive", main_archive),
    ".tar": ("Archive", main_archive), ".gz": ("Archive", main_archive), ".bz2": ("Archive", main_archive),

    # E-book Formats
    ".epub": ("E-book", main_ebook), ".mobi": ("E-book", main_ebook), ".azw3": ("E-book", main_ebook),
    ".fb2": ("E-book", main_ebook),

    # Font Formats
    ".ttf": ("Font", main_font), ".otf": ("Font", main_font), ".woff": ("Font", main_font),
    ".woff2": ("Font", main_font),
}


def identify_and_run_converter(file_path):
    """Identifies the file type from its extension and runs the correct converter."""
    
    # Extract the file extension
    _, extension = os.path.splitext(file_path)
    extension = extension.lower() # Standardize to lowercase

    # Look up the extension in our mapping
    converter_info = FILE_TYPE_MAPPING.get(extension)

    if converter_info:
        file_type, converter_function = converter_info
        
        # Announce which module is being launched
        console.print(Panel(
            f"Detected an [bold green]{file_type}[/] file.\nLaunching the [bold green]{file_type} Converter[/] for you...",
            title="[bold yellow]File Type Detected[/]",
            border_style="yellow",
            padding=(1, 2)
        ))
        
        # Call the appropriate main function, PASSING the file path
        converter_function(input_file_path=file_path)
    else:
        # If the extension is not found in our mapping
        console.print(Panel(
            f"Could not identify the file type for extension '[bold red]{extension}[/]'.\n"
            "This program cannot process this file.",
            title="[bold red]Unknown File Type[/]",
            border_style="red"
        ))


if __name__ == '__main__':
    console.print(Panel(
        "[bold green]🐍 Welcome to the Universal File Converter 🐍[/]\n"
        "[cyan]Simply enter the path to any file, and this script will open the right tool for the job.[/]",
        title="[bold yellow]All-In-One Converter[/]",
        border_style="green",
        padding=(1, 2)
    ))

    # Get the file path from the user
    while True:
        input_file = Prompt.ask("\n[bold yellow]➡️  Enter the path to the file you want to convert[/]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_file) and os.path.isfile(input_file):
            break
        console.print("❌ [bold red]ERROR: That file does not exist. Please check the path and try again.[/]")
        
    # Let the magic happen!
    identify_and_run_converter(input_file)

    console.print(Panel(
        "[bold green]Task complete. Thank you for using the Universal Converter![/]",
        title="[bold yellow]Finished[/]",
        border_style="green"
    ))
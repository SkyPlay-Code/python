import os
import shutil
import time
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# RICH: Import the necessary components from the rich library
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# RICH: Define a custom theme for consistent styling
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "prompt": "bold yellow",
    "path": "bold cyan",
    "format": "bold blue",
})

# RICH: Initialize the console with our theme
console = Console(theme=custom_theme)


# --- DATA ENHANCEMENT 1: More detailed format descriptions ---
# Each format is now a dictionary with details for the table.
SUPPORTED_FORMATS = {
    # --- Popular Lossy Formats ---
    "MP3": {"id": "mp3", "ext": "mp3", "type": "[orange3]Lossy[/]", "desc": "Most common audio format. Great compatibility."},
    "AAC": {"id": "aac", "ext": "aac", "type": "[orange3]Lossy[/]", "desc": "Modern alternative to MP3. Good for streaming."},
    "OGG": {"id": "ogg", "ext": "ogg", "type": "[orange3]Lossy[/]", "desc": "Open-source and patent-free. Great for web."},
    "Opus": {"id": "opus", "ext": "opus", "type": "[orange3]Lossy[/]", "desc": "Excellent for voice & low-latency (e.g., Discord)."},
    "WMA": {"id": "wma", "ext": "wma", "type": "[orange3]Lossy[/]", "desc": "Windows Media Audio. Good for Windows ecosystem."},
    "AC3": {"id": "ac3", "ext": "ac3", "type": "[orange3]Lossy[/]", "desc": "Dolby Digital audio, used for video soundtracks."},
    "M4A": {"id": "ipod", "ext": "m4a", "type": "[orange3]Lossy[/]", "desc": "Apple's standard container for AAC audio."},

    # --- Popular Lossless & Uncompressed Formats ---
    "FLAC": {"id": "flac", "ext": "flac", "type": "[green]Lossless[/]", "desc": "Perfect, CD-quality archival format."},
    "WAV": {"id": "wav", "ext": "wav", "type": "[green]Uncompressed[/]", "desc": "Studio-quality master format. Very large files."},
    "AIFF": {"id": "aiff", "ext": "aiff", "type": "[green]Uncompressed[/]", "desc": "Apple's equivalent of WAV."},
    "ALAC": {"id": "alac", "ext": "m4a", "type": "[green]Lossless[/]", "desc": "Apple's lossless format. iTunes friendly."},
}

# --- DATA ENHANCEMENT 2: More detailed bitrate descriptions ---
BITRATE_OPTIONS = {
    "mp3": [
        {"rate": "128k", "desc": "Standard Quality - Good for podcasts, small size."},
        {"rate": "192k", "desc": "High Quality - Standard for music listening."},
        {"rate": "256k", "desc": "Excellent Quality - For audiophiles."},
        {"rate": "320k", "desc": "Near-CD Quality - Virtually indistinguishable lossy."},
    ],
    "aac": [
        {"rate": "128k", "desc": "Good Quality - Great for mobile devices."},
        {"rate": "192k", "desc": "High Quality - Excellent for music streaming."},
        {"rate": "256k", "desc": "Excellent Quality - Transparent, high-fidelity sound."},
        {"rate": "320k", "desc": "Archival Quality - Top-tier for AAC format."},
    ],
    # You can add similar detailed lists for "ogg", "opus", and "wma" here
}
# Fallback for formats without a detailed list
BITRATE_OPTIONS.setdefault("ogg", [{"rate": r, "desc": f"Bitrate: {r}"} for r in ["128k", "192k", "256k", "320k"]])
BITRATE_OPTIONS.setdefault("opus", [{"rate": r, "desc": f"Bitrate: {r}"} for r in ["96k", "128k", "192k", "256k"]])
BITRATE_OPTIONS.setdefault("wma", [{"rate": r, "desc": f"Bitrate: {r}"} for r in ["128k", "192k", "256k", "320k"]])


def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Audio Converter 🐍[/]\n[cyan]A stylish, user-friendly tool powered by FFmpeg & Rich[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not is_ffmpeg_installed():
        console.print(Panel(
            "[warning]FFmpeg is not found in your system's PATH.[/warning]\nThis script requires FFmpeg for audio processing.\nPlease install it from [bold blue underline]https://ffmpeg.org/download.html[/]",
            title="[danger]Dependency Warning[/]", border_style="red", padding=(1, 2)
        ))

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your audio file[/prompt]").strip().replace("'", "").replace('"', '')
        if not os.path.exists(input_path):
            console.print("❌ [danger]ERROR: File not found. Please check the path and try again.[/]")
        elif not os.path.isfile(input_path):
            console.print(f"❌ [danger]ERROR: The path '[path]{input_path}[/]' is a directory, not a file.[/]")
        else:
            return input_path

def get_output_format():
    """RICH: Display formats in a detailed, multi-column table."""
    table = Table(title="[bold green]✅ Select an Output Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format Name", style="bold blue", min_width=6)
    table.add_column("Extension", style="magenta", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Description", style="dim cyan", min_width=20) # Give description more space

    format_list = list(SUPPORTED_FORMATS.items())
    
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(
            str(i), 
            name, 
            f".{details['ext']}", 
            details['type'], 
            details['desc']
        )
        
    console.print(table)
    
    while True:
        try:
            choice_str = Prompt.ask("[prompt]➡️  Enter the number for your choice[/prompt]")
            choice = int(choice_str)
            if 1 <= choice <= len(format_list):
                # Return the ffmpeg identifier from the nested dictionary
                return format_list[choice - 1][1]['id']
            else:
                console.print(f"[danger]❌ ERROR: Invalid choice. Please enter a number between 1 and {len(format_list)}.[/]")
        except ValueError:
            console.print("[danger]❌ ERROR: Please enter a valid number.[/]")

def get_bitrate(output_format):
    """RICH: Display detailed bitrate options in a table."""
    if output_format in BITRATE_OPTIONS:
        options = BITRATE_OPTIONS[output_format]
        ext = next((v['ext'] for k, v in SUPPORTED_FORMATS.items() if v['id'] == output_format), output_format) # Find display extension
        
        table = Table(title=f"[bold green]✅ Select Quality for [format].{ext.upper()}[/]", border_style="cyan")
        table.add_column("Num", style="bold yellow", justify="center")
        table.add_column("Bitrate", style="magenta", justify="center")
        table.add_column("Description", style="dim")
        
        for i, opt in enumerate(options, 1):
            table.add_row(str(i), opt['rate'], opt['desc'])

        console.print(table)

        while True:
            try:
                # Set a reasonable default choice (e.g., the second option)
                default_choice = "2" if len(options) > 1 else "1"
                choice_str = Prompt.ask(f"[prompt]➡️  Enter number for your choice (default is {default_choice})[/prompt]", default=default_choice)
                choice = int(choice_str)
                if 1 <= choice <= len(options):
                    # Return the bitrate value from the list of dictionaries
                    return options[choice - 1]['rate']
                else:
                    console.print(f"[danger]❌ ERROR: Please enter a number between 1 and {len(options)}.[/]")
            except ValueError:
                console.print("[danger]❌ ERROR: Please enter a valid number.[/]")
    return None

def convert_audio(input_file_path, output_format, bitrate=None):
    """Handles the core audio conversion logic with a rich progress bar."""
    # Find the correct output extension from our detailed dictionary
    output_extension = next((v['ext'] for k, v in SUPPORTED_FORMATS.items() if v['id'] == output_format), output_format)
    
    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = f"{base_name}_converted.{output_extension}"

    summary_panel = Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Output Format:[/info] [format]{output_extension.upper()}[/]\n"
        f"[info]Quality/Bitrate:[/info] [format]{bitrate or 'Lossless/Default'}[/]\n"
        f"[info]Output File:[/info] [path]{os.path.basename(output_file_path)}[/]",
        title="[bold yellow]Conversion Summary[/]",
        border_style="yellow"
    )
    console.print(summary_panel)

    try:
        #RICH: Use a progress bar while the file is being processed.
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            transient=True, # The bar will disappear on completion
        ) as progress:
            task = progress.add_task("[green]Processing...", total=100)
            
            # Since pydub doesn't provide progress, we simulate it
            progress.update(task, advance=10, description="Reading audio file...")
            audio = AudioSegment.from_file(input_file_path)
            progress.update(task, advance=30, description="Exporting with FFmpeg...")

            export_params = {'format': output_format}
            if bitrate:
                export_params['bitrate'] = bitrate
            audio.export(output_file_path, **export_params)
            
            progress.update(task, advance=60, description="[bold green]Finalizing...[/]")
            time.sleep(0.5)

        console.print(Panel(
            f"🎉 [success]Success! Conversion complete.[/] 🎉\n[info]New file saved at:[/info] [path]{output_file_path}[/]",
            title="[bold green]Complete[/]",
            border_style="green"
        ))

    except CouldntDecodeError:
        console.print(Panel(
            "[danger]CRITICAL ERROR: Could not decode the input file.[/danger]\n"
            "[warning]The file might be corrupted, or it might be an unsupported format.[/]",
            title="[bold red]Conversion Failed[/]", border_style="red"
        ))
    except Exception as e:
        console.print(Panel(
            f"[danger]AN UNEXPECTED ERROR OCCURRED: {e}[/]\n"
            "[warning]Please ensure FFmpeg is installed and accessible in your system's PATH.[/]",
            title="[bold red]Conversion Failed[/]", border_style="red"
        ))


# The new main function that can accept a file path
def main(input_file_path=None):
    """The main execution function for the audio converter."""
    display_intro()
    if not is_ffmpeg_installed():
        Prompt.ask("\n[prompt]Press Enter to exit.[/prompt]")
        return

    # If a file path isn't passed in, ask the user for it.
    if not input_file_path:
        input_file_path = get_input_file()
    else:
        # If a file was passed in, just confirm it to the user.
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Audio Converter[/]", border_style="green"))

    output_format = get_output_format()
    bitrate = get_bitrate(output_format)
    convert_audio(input_file_path, output_format, bitrate)

# The new, simpler __main__ block that allows the script to still be run directly
if __name__ == '__main__':
    main()
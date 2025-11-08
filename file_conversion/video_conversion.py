import os
import sys
import shutil
import ffmpeg

# RICH: Import the necessary components from the rich library
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.status import Status

# RICH: Define a custom theme for consistent styling
custom_theme = Theme({
    "info": "dim cyan", "warning": "magenta", "danger": "bold red",
    "success": "bold green", "prompt": "bold yellow", "path": "bold cyan",
    "format": "bold blue",
})
console = Console(theme=custom_theme)

# --- NEW DATA STRUCTURES: Separate dictionaries for each output type ---
VIDEO_OUTPUT_FORMATS = {
    "MP4": {"id": "mp4", "type": "[green]Web & General Use[/]", "desc": "The most widely compatible format for web, mobile, and streaming."},
    "MKV": {"id": "mkv", "type": "[green]General Use[/]", "desc": "Flexible container. Great for holding multiple audio/subtitle tracks."},
    "WebM": {"id": "webm", "type": "[green]Web Use[/]", "desc": "Open-source, royalty-free format designed for the web. Great for HTML5 video."},
    "MOV": {"id": "mov", "type": "[blue]Editing & Apple[/]", "desc": "Apple's QuickTime format. High quality, often used in video editing."},
    "AVI": {"id": "avi", "type": "[yellow]Legacy[/]", "desc": "An older, but still widely supported, standard Windows container."},
    "OGV": {"id": "ogv", "type": "[green]Web Use[/]", "desc": "Open-source video container, part of the Ogg project."},
}

AUDIO_OUTPUT_FORMATS = {
    "MP3": {"id": "mp3", "bitrate": "192k", "desc": "Best compatibility for audio extraction."},
    "WAV": {"id": "wav", "bitrate": None, "desc": "Uncompressed, studio-quality audio."},
    "AAC": {"id": "aac", "bitrate": "192k", "desc": "Modern audio format, great for Apple devices."},
    "OGG": {"id": "ogg", "bitrate": "192k", "desc": "Open-source audio format."},
}

GIF_OUTPUT_FORMATS = {
    "GIF": {"id": "gif", "desc": "Standard Animated GIF. Universally supported."},
}

# --- MODIFIED: Added more quality levels ---
QUALITY_LEVELS = {
    "1": {"crf": "18", "preset": "slow", "label": "Excellent Quality", "desc": "Great for final exports. Slower encoding, larger files."},
    "2": {"crf": "23", "preset": "medium", "label": "Good Quality (Recommended)", "desc": "A balanced trade-off between quality, speed, and file size."},
    "3": {"crf": "28", "preset": "fast", "label": "Draft Quality", "desc": "Lower quality, smaller files. Ideal for quick previews or tests."},
    "4": {"crf": "32", "preset": "ultrafast", "label": "Low Quality (Smallest Size)", "desc": "Very high compression. Noticeable quality loss, but very small files."},
}

def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Video Converter 🐍[/]\n[cyan]A powerful tool for converting videos, extracting audio, and creating GIFs[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not is_ffmpeg_installed():
        console.print(Panel("[danger]CRITICAL: FFmpeg is not found...", title="[bold red]Dependency Missing[/]", border_style="red"))
        sys.exit(1)

def get_input_file():
    # This function is kept for when the script is run directly, but won't be used by main.py
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your video file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path): return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

# --- NEW: A top-level menu to choose the conversion CATEGORY ---
def get_conversion_type():
    """Asks the user what kind of conversion they want to perform."""
    table = Table(title="[bold green]✅ What would you like to do with this video?[/]", border_style="cyan")
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Action", style="bold blue")
    table.add_column("Description", style="dim cyan")
    
    table.add_row("1", "Convert to another Video Format", "Change the video's container (e.g., MP4 to MKV) and re-encode it.")
    table.add_row("2", "Extract Audio", "Save only the sound from the video into an audio file (e.g., MP3, WAV).")
    table.add_row("3", "Create Animated GIF", "Convert the video into a looping, silent GIF animation.")

    console.print(table)
    choice = IntPrompt.ask("[prompt]➡️  Enter the number for your choice[/prompt]", choices=["1", "2", "3"])
    if choice == 1: return "video"
    if choice == 2: return "audio"
    if choice == 3: return "gif"

def get_output_format(format_dict):
    """A generic function to get the format from any of our format dictionaries."""
    table = Table(title="[bold green]✅ Select an Output Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Description", style="dim cyan")

    format_list = list(format_dict.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['desc'])
        
    console.print(table)
    choice = IntPrompt.ask("[prompt]➡️  Enter number[/prompt]", choices=[str(i) for i in range(1, len(format_list) + 1)])
    return format_list[choice - 1][1]

def get_quality_setting():
    # This function remains largely the same, but now has 4 options
    table = Table(title="[bold green]✅ Select an Encoding Quality Setting[/]", border_style="cyan")
    table.add_column("Num", "Quality Level", "Description", style="bold yellow", justify="center")
    for key, value in QUALITY_LEVELS.items():
        table.add_row(key, f"[magenta]{value['label']}[/]", f"[dim]{value['desc']}[/]")
    console.print(table)
    choice = Prompt.ask("[prompt]➡️  Enter number (default is 2)[/prompt]", choices=QUALITY_LEVELS.keys(), default="2")
    return QUALITY_LEVELS[choice]

# --- NEW: Refactored conversion logic into separate functions ---
def run_conversion(input_file_path, output_path, ffmpeg_stream, summary_panel):
    """Generic function to run ffmpeg and display status and results."""
    console.print(summary_panel)
    with Status("[bold green]Converting... this may take a while. FFmpeg is at work![/]", spinner="dots"):
        try:
            ffmpeg.run(ffmpeg_stream, overwrite_output=True, quiet=True)
            console.print(Panel(
                f"🎉 [success]Success! Conversion complete.[/] 🎉\n[info]New file saved at:[/info] [path]{output_path}[/]",
                title="[bold green]Complete[/]", border_style="green"
            ))
        except ffmpeg.Error as e:
            console.print(Panel(
                f"[danger]FFmpeg encountered a critical error.[/]\n[dim]{e.stderr.decode('utf-8', errors='ignore')}[/]",
                title="[bold red]Conversion Failed[/]", border_style="red"
            ))
        except Exception as e:
            console.print(Panel(f"[danger]AN UNEXPECTED ERROR: {e}[/]", title="[bold red]Conversion Failed[/]"))

# --- MODIFIED: The main function is now a router ---
def main(input_file_path=None):
    display_intro()
    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]", title="[bold green]Starting Video Converter[/]"))

    conversion_type = get_conversion_type()
    base_name = os.path.splitext(input_file_path)[0]
    stream = ffmpeg.input(input_file_path)

    # --- ROUTE 1: Video -> Video ---
    if conversion_type == "video":
        details = get_output_format(VIDEO_OUTPUT_FORMATS)
        quality = get_quality_setting()
        output_path = f"{base_name}_converted.{details['id']}"
        summary = Panel(f"[info]Action:[/info] [format]Video Conversion[/]\n"
                        f"[info]Output Format:[/info] [format]{details['id'].upper()}[/]\n"
                        f"[info]Quality Level:[/info] [format]{quality['label']}[/]\n"
                        f"[info]Output File:[/info] [path]{os.path.basename(output_path)}[/]",
                        title="[bold yellow]Conversion Summary[/]")
        ffmpeg_stream = ffmpeg.output(stream.video, stream.audio, output_path,
                                      vcodec='libx264', acodec='aac',
                                      crf=quality['crf'], preset=quality['preset'])
        run_conversion(input_file_path, output_path, ffmpeg_stream, summary)

    # --- ROUTE 2: Video -> Audio ---
    elif conversion_type == "audio":
        details = get_output_format(AUDIO_OUTPUT_FORMATS)
        output_path = f"{base_name}_audio.{details['id']}"
        summary = Panel(f"[info]Action:[/info] [format]Audio Extraction[/]\n"
                        f"[info]Output Format:[/info] [format]{details['id'].upper()}[/]\n"
                        f"[info]Output File:[/info] [path]{os.path.basename(output_path)}[/]",
                        title="[bold yellow]Conversion Summary[/]")
        # For audio, we only specify audio codecs and bitrate
        ffmpeg_stream = ffmpeg.output(stream.audio, output_path,
                                      acodec='libmp3lame' if details['id'] == 'mp3' else details['id'],
                                      audio_bitrate=details['bitrate'])
        run_conversion(input_file_path, output_path, ffmpeg_stream, summary)
        
    # --- ROUTE 3: Video -> GIF ---
    elif conversion_type == "gif":
        details = get_output_format(GIF_OUTPUT_FORMATS)
        output_path = f"{base_name}_animation.{details['id']}"
        summary = Panel(f"[info]Action:[/info] [format]GIF Creation[/]\n"
                        f"[info]Output Format:[/info] [format]{details['id'].upper()}[/]\n"
                        f"[info]Output File:[/info] [path]{os.path.basename(output_path)}[/]",
                        title="[bold yellow]Conversion Summary[/]")
        # For GIF, we only take the video stream and have no audio.
        ffmpeg_stream = ffmpeg.output(stream.video, output_path)
        run_conversion(input_file_path, output_path, ffmpeg_stream, summary)

if __name__ == '__main__':
    main()
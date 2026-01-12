import os
import sys
import ffmpeg  # This requires 'pip install ffmpeg-python'
import imageio_ffmpeg

# RICH: Import the necessary components from the rich library
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.status import Status

# --- DEPENDENCY CHECK ---
# This catches the specific error you were facing
if not hasattr(ffmpeg, 'input'):
    print("\nCRITICAL ERROR: Wrong library installed.")
    print("Please run: pip uninstall ffmpeg")
    print("Then run:   pip install ffmpeg-python")
    sys.exit(1)

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# RICH: Define a custom theme
custom_theme = Theme({
    "info": "dim cyan", "warning": "magenta", "danger": "bold red",
    "success": "bold green", "prompt": "bold yellow", "path": "bold cyan",
    "format": "bold blue",
})
console = Console(theme=custom_theme)

# --- DATA STRUCTURES ---
VIDEO_OUTPUT_FORMATS = {
    "MP4": {"id": "mp4", "type": "[green]Web & General Use[/]", "desc": "Most compatible. Uses H.264/AAC."},
    "MKV": {"id": "mkv", "type": "[green]General Use[/]", "desc": "Flexible container. Good for archiving."},
    "WebM": {"id": "webm", "type": "[green]Web Use[/]", "desc": "Open-source, HTML5 friendly."},
    "MOV": {"id": "mov", "type": "[blue]Apple/Editing[/]", "desc": "QuickTime format."},
    "AVI": {"id": "avi", "type": "[yellow]Legacy[/]", "desc": "Older Windows standard."},
}

# UPDATED: Added specific 'codec' keys so ffmpeg knows exactly what to do
AUDIO_OUTPUT_FORMATS = {
    "MP3": {"id": "mp3", "codec": "libmp3lame", "bitrate": "192k", "desc": "Universal compatibility."},
    "WAV": {"id": "wav", "codec": "pcm_s16le", "bitrate": None, "desc": "Uncompressed CD quality."},
    "AAC": {"id": "aac", "codec": "aac", "bitrate": "192k", "desc": "Standard for MP4/Apple."},
    "OGG": {"id": "ogg", "codec": "libvorbis", "bitrate": "192k", "desc": "Open source audio."},
}

GIF_OUTPUT_FORMATS = {
    "GIF": {"id": "gif", "desc": "Animated GIF image."},
}

QUALITY_LEVELS = {
    "1": {"crf": "18", "preset": "slow", "label": "Excellent", "desc": "High quality, larger file."},
    "2": {"crf": "23", "preset": "medium", "label": "Good (Recommended)", "desc": "Balanced quality/size."},
    "3": {"crf": "28", "preset": "fast", "label": "Draft", "desc": "Lower quality, fast encode."},
    "4": {"crf": "32", "preset": "ultrafast", "label": "Low", "desc": "Smallest size, visible blockiness."},
}

def is_ffmpeg_installed():
    return os.path.exists(FFMPEG_PATH)

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Python Video Converter 🐍[/]\n[cyan]Powered by ffmpeg-python & imageio[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not is_ffmpeg_installed():
        console.print(Panel("[danger]CRITICAL: FFmpeg binary not found.[/]", title="Dependency Error"))
        sys.exit(1)

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your video file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path): return input_path
        console.print("❌ [danger]ERROR: File not found.[/]")

def get_conversion_type():
    table = Table(title="[bold green]Select Action[/]", border_style="cyan")
    table.add_column("No.", style="bold yellow", justify="center")
    table.add_column("Action", style="bold blue")
    table.add_column("Description", style="dim cyan")
    
    table.add_row("1", "Convert Video", "Change format (MP4, MKV, etc.)")
    table.add_row("2", "Extract Audio", "Save audio only (MP3, WAV, etc.)")
    table.add_row("3", "Create GIF", "Make a silent animation")

    console.print(table)
    choice = IntPrompt.ask("[prompt]➡️  Choice[/prompt]", choices=["1", "2", "3"])
    mapping = {1: "video", 2: "audio", 3: "gif"}
    return mapping[choice]

def get_output_format(format_dict):
    table = Table(title="[bold green]Select Format[/]", border_style="cyan")
    table.add_column("No.", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Description", style="dim cyan")

    format_list = list(format_dict.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['desc'])
        
    console.print(table)
    choice = IntPrompt.ask("[prompt]➡️  Choice[/prompt]", choices=[str(i) for i in range(1, len(format_list) + 1)])
    return format_list[choice - 1][1]

def get_quality_setting():
    table = Table(title="[bold green]Select Quality[/]", border_style="cyan")
    table.add_column("No.", "Level", "Description", style="bold yellow")
    for key, value in QUALITY_LEVELS.items():
        table.add_row(key, f"[magenta]{value['label']}[/]", f"[dim]{value['desc']}[/]")
    console.print(table)
    choice = Prompt.ask("[prompt]➡️  Choice (default: 2)[/prompt]", choices=QUALITY_LEVELS.keys(), default="2")
    return QUALITY_LEVELS[choice]

def run_conversion(ffmpeg_stream, output_path, summary_panel):
    console.print(summary_panel)
    
    with Status("[bold green]Processing... (This usually takes time)[/]", spinner="dots"):
        try:
            # We must pass the manual executable path from imageio
            ffmpeg.run(ffmpeg_stream, overwrite_output=True, quiet=True, cmd=FFMPEG_PATH)
            
            console.print(Panel(
                f"🎉 [success]Success![/] File saved:\n[path]{output_path}[/]",
                title="[bold green]Done[/]", border_style="green"
            ))
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else "Unknown FFmpeg error"
            console.print(Panel(
                f"[danger]Conversion Failed[/]\n[dim]{error_msg}[/]",
                title="[bold red]Error[/]", border_style="red"
            ))
        except Exception as e:
            console.print(Panel(f"[danger]Unexpected Error: {e}[/]", title="[bold red]Exception[/]"))

def main(input_file_path=None):
    display_intro()
    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"Input: [path]{input_file_path}[/]", title="[bold green]File Loaded[/]"))

    conversion_type = get_conversion_type()
    base_name = os.path.splitext(input_file_path)[0]
    
    # Initialize the input stream
    stream = ffmpeg.input(input_file_path)

    # --- ROUTE 1: Video -> Video ---
    if conversion_type == "video":
        fmt = get_output_format(VIDEO_OUTPUT_FORMATS)
        qual = get_quality_setting()
        output_path = f"{base_name}_converted.{fmt['id']}"
        
        summary = Panel(f"[info]Mode:[/info] Video Conversion\n[info]Target:[/info] {fmt['id'].upper()}\n[info]Quality:[/info] {qual['label']}", title="Summary")
        
        # We pass 'stream' (the whole container) instead of stream.video/stream.audio
        # This prevents errors if the input file has no audio.
        ffmpeg_stream = ffmpeg.output(stream, output_path,
                                      vcodec='libx264', acodec='aac',
                                      crf=qual['crf'], preset=qual['preset'])
        
        run_conversion(ffmpeg_stream, output_path, summary)

    # --- ROUTE 2: Video -> Audio ---
    elif conversion_type == "audio":
        fmt = get_output_format(AUDIO_OUTPUT_FORMATS)
        output_path = f"{base_name}_audio.{fmt['id']}"
        
        summary = Panel(f"[info]Mode:[/info] Audio Extraction\n[info]Target:[/info] {fmt['id'].upper()}", title="Summary")
        
        # Build arguments based on format requirements
        kwargs = {'acodec': fmt['codec']}
        if fmt['bitrate']:
            kwargs['audio_bitrate'] = fmt['bitrate']
            
        ffmpeg_stream = ffmpeg.output(stream.audio, output_path, **kwargs)
        run_conversion(ffmpeg_stream, output_path, summary)
        
    # --- ROUTE 3: Video -> GIF ---
    elif conversion_type == "gif":
        fmt = get_output_format(GIF_OUTPUT_FORMATS)
        output_path = f"{base_name}_anim.{fmt['id']}"
        
        summary = Panel(f"[info]Mode:[/info] GIF Creation", title="Summary")
        
        # Basic GIF creation. 
        # For better results in production, one would usually add palettegen/paletteuse filters,
        # but this keeps it simple and functional.
        ffmpeg_stream = ffmpeg.output(stream.video, output_path)
        run_conversion(ffmpeg_stream, output_path, summary)

if __name__ == '__main__':
    # If run directly
    main()
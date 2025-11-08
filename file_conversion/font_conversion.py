import os
import sys

# RICH: Import necessary components BEFORE checking for the FontForge import
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# RICH: Define theme and console
custom_theme = Theme({
    "info": "dim cyan", "warning": "magenta", "danger": "bold red",
    "success": "bold green", "prompt": "bold yellow", "path": "bold cyan",
    "format": "bold blue",
})
console = Console(theme=custom_theme)

# Check for FontForge module import
try:
    import fontforge
    FONTFORGE_AVAILABLE = True
except ImportError:
    FONTFORGE_AVAILABLE = False


# --- DATA ENHANCEMENT: Detailed format descriptions ---
SUPPORTED_FORMATS = {
    # --- Modern Desktop & Web Formats ---
    "TTF": {"ext": "ttf", "gen": True, "type": "[green]Desktop & Web[/]", "desc": "TrueType Font. Universally compatible standard."},
    "OTF": {"ext": "otf", "gen": True, "type": "[green]Desktop & Print[/]", "desc": "OpenType Font. Often has more advanced features for design."},
    "WOFF2": {"ext": "woff2", "gen": True, "type": "[blue]Modern Web[/]", "desc": "Best compression for web fonts. The modern standard."},
    "WOFF": {"ext": "woff", "gen": True, "type": "[blue]Web[/]", "desc": "Web Open Font Format. Excellent for web use, widely supported."},

    # --- Font Development & Legacy Formats ---
    "UFO": {"ext": "ufo", "gen": True, "type": "[cyan]Development[/]", "desc": "Unified Font Object. XML-based source format for font design."},
    "SFD": {"ext": "sfd", "gen": False, "type": "[cyan]Development[/]", "desc": "Spline Font Database. FontForge's native project file."},
    "PFB": {"ext": "pfb", "gen": True, "type": "[yellow]Legacy PostScript[/]", "desc": "PostScript Type 1 (Binary). Older format for professional printing."},
    "DFONT": {"ext": "dfont", "gen": True, "type": "[yellow]Legacy Apple[/]", "desc": "Datafork TrueType Suitcase used on classic Mac OS."},
    
    # --- Metrics Formats ---
    "AFM": {"ext": "afm", "gen": False, "type": "[white]Metrics Data[/]", "desc": "Adobe Font Metrics. Text file describing the font's measurements."},
}

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Font Converter 🐍[/]\n[cyan]A precision tool for converting font files using the FontForge engine[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not FONTFORGE_AVAILABLE:
        console.print(Panel(
            "[danger]CRITICAL ERROR: The 'fontforge' Python module could not be found.[/]\n"
            "This script is a wrapper for FontForge and cannot function without it.\n\n"
            "[info]Common Fixes:[/]\n"
            "[dim]• [bold]macOS[/]: `brew install fontforge`\n"
            "• [bold]Linux (Debian/Ubuntu)[/]: `sudo apt-get install python3-fontforge`\n"
            "• [bold]Windows[/]: Ensure FontForge is installed and its Python path is configured.[/]",
            title="[bold red]Dependency Missing[/]", border_style="red"
        ))
        sys.exit(1)

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your font file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path):
            return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

def get_output_format():
    """RICH: Displays font format options in a detailed table."""
    table = Table(title="[bold green]✅ Select an Output Font Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Type / Use Case", style="white")
    table.add_column("Description", style="dim cyan")
    
    format_list = list(SUPPORTED_FORMATS.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['type'], details['desc'])
        
    console.print(table)
    
    choice = IntPrompt.ask(
        "[prompt]➡️  Enter the number for your choice[/prompt]",
        choices=[str(i) for i in range(1, len(format_list) + 1)]
    )
    # Return the details dictionary for the chosen format
    return format_list[choice - 1][1]

def convert_font(input_file_path, output_details):
    output_ext = output_details['ext']
    is_generate_target = output_details['gen']
    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = f"{base_name}_converted.{output_ext}"
    
    console.print(Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Output Format:[/info] [format]{output_ext.upper()}[/]",
        title="[bold yellow]Conversion Summary[/]", border_style="yellow"
    ))
    
    try:
        # RICH: Use a progress bar for responsive feedback
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), transient=True) as progress:
            task = progress.add_task("[green]Converting...", total=100)
            
            progress.update(task, description="Opening font file with FontForge...", advance=25)
            font = fontforge.open(input_file_path)
            
            action_verb = "Generating" if is_generate_target else "Saving"
            progress.update(task, description=f"{action_verb} new font file...", advance=50)
            
            if is_generate_target:
                font.generate(output_file_path)
            else:
                font.save(output_file_path)
                
            progress.update(task, description="Done!", completed=100)
            
        console.print(Panel(
            f"🎉 [success]Success! Font conversion complete.[/] 🎉\n[info]New file saved at:[/info] [path]{output_file_path}[/]",
            title="[bold green]Complete[/]", border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[danger]FontForge failed to convert the file.[/]\n"
            f"[warning]The input font may be corrupted, password-protected, or unsupported.[/]\n\n"
            f"[bold]Error Details from FontForge:[/]\n[dim]{e}[/dim]",
            title="[bold red]Conversion Failed[/]", border_style="red"
        ))


def main(input_file_path=None):
    """The main execution function for the font converter."""
    display_intro()

    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Font Converter[/]", border_style="green"))

    output_format_details = get_output_format()
    convert_font(input_file_path, output_format_details)

if __name__ == '__main__':
    main()
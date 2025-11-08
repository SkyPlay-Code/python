import os
import sys
import shutil
import subprocess

# RICH: Import necessary components
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.status import Status

# RICH: Define theme and console
custom_theme = Theme({
    "info": "dim cyan", "warning": "magenta", "danger": "bold red",
    "success": "bold green", "prompt": "bold yellow", "path": "bold cyan",
    "format": "bold blue",
})
console = Console(theme=custom_theme)


# --- DATA ENHANCEMENT: Detailed format descriptions ---
SUPPORTED_FORMATS = {
    # --- Modern & Common E-reader Formats ---
    "EPUB": {"id": "epub", "for": "[green]Most E-readers[/]", "desc": "The universal standard. Works on Kobo, Nook, and most devices except Kindle."},
    "AZW3": {"id": "azw3", "for": "[bold orange3]Amazon Kindle[/]", "desc": "Modern Kindle format. Best choice for current Kindle devices."},
    "MOBI": {"id": "mobi", "for": "[orange3]Older Kindle[/]", "desc": "Older Kindle format. Good for compatibility with older devices."},
    
    # --- Other Formats ---
    "PDF": {"id": "pdf", "for": "[blue]Computers & Tablets[/]", "desc": "Preserves exact layout. Best for large screens, not ideal for e-ink."},
    "FB2": {"id": "fb2", "for": "[yellow]Various[/]", "desc": "FictionBook. Popular in Eastern Europe, supported by some apps."},
    "LRF": {"id": "lrf", "for": "[yellow]Legacy Sony[/]", "desc": "Older, proprietary format for Sony Reader devices."},
    "PDB": {"id": "pdb", "for": "[yellow]Legacy Palm[/]", "desc": "Format used by Palm Pilot and some older e-reader apps."},
    "TXT": {"id": "txt", "for": "[white]Universal Text[/]", "desc": "Extracts plain text content. Removes all formatting and images."},
}

def get_calibre_path():
    """Finds the path to Calibre's 'ebook-convert' executable."""
    if sys.platform == "win32":
        # Check both common Program Files locations on Windows
        for path in ("C:\\Program Files\\Calibre2\\ebook-convert.exe", "C:\\Program Files\\Calibre\\ebook-convert.exe"):
            if os.path.exists(path): return path
    elif sys.platform == "darwin":
        path = "/Applications/calibre.app/Contents/MacOS/ebook-convert"
        if os.path.exists(path): return path
    return shutil.which("ebook-convert")

CALIBRE_PATH = get_calibre_path()

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python E-book Converter 🐍[/]\n[cyan]A high-quality conversion tool powered by the Calibre engine[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not CALIBRE_PATH:
        console.print(Panel(
            "[danger]CRITICAL: Calibre's 'ebook-convert' tool was not found.[/]\n"
            "This script is a wrapper for Calibre and cannot function without it.\n"
            "Please install it from [bold blue underline]https://calibre-ebook.com/download[/]",
            title="[bold red]Dependency Missing[/]", border_style="red"
        ))
        sys.exit(1)

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your e-book file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path):
            return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

def get_output_format():
    """RICH: Displays e-book format options in a detailed table."""
    table = Table(title="[bold green]✅ Select an Output E-book Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Best For", style="white")
    table.add_column("Description", style="dim cyan")
    
    format_list = list(SUPPORTED_FORMATS.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['for'], details['desc'])
        
    console.print(table)
    
    choice = IntPrompt.ask(
        "[prompt]➡️  Enter the number for your choice[/prompt]",
        choices=[str(i) for i in range(1, len(format_list) + 1)]
    )
    return format_list[choice - 1][1]['id']

def convert_ebook(input_file_path, output_format):
    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = f"{base_name}_converted.{output_format}"
    
    console.print(Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Output Format:[/info] [format]{output_format.upper()}[/]",
        title="[bold yellow]Conversion Summary[/]", border_style="yellow"
    ))

    command = [CALIBRE_PATH, input_file_path, output_file_path]
    
    # RICH: Use console.status for feedback during the external process
    with console.status("[bold green]Calibre is processing your e-book...[/]", spinner="dots") as status:
        try:
            # Run the command, capturing output
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            
            console.print(Panel(
                f"🎉 [success]Success! E-book conversion complete.[/] 🎉\n[info]New file saved at:[/info] [path]{output_file_path}[/]",
                title="[bold green]Complete[/]", border_style="green"
            ))

        except FileNotFoundError:
            console.print(Panel("[danger]CRITICAL ERROR: Could not find the Calibre executable.[/]\n",
                          title="[bold red]Error[/]", border_style="red"))
        except subprocess.CalledProcessError as e:
            # Check for common DRM error message from Calibre
            error_output = e.stdout + e.stderr
            if "DRM" in error_output:
                drm_message = "[bold]This book has DRM (Digital Rights Management).[/]\nCalibre cannot convert DRM-protected e-books."
            else:
                drm_message = "[warning]The file may be corrupted, password-protected, or unsupported.[/]"

            console.print(Panel(
                f"[danger]Calibre failed to convert the file.[/]\n{drm_message}\n\n"
                f"[bold]Error Details from Calibre:[/]\n[dim]{error_output}[/dim]",
                title="[bold red]Conversion Failed[/]", border_style="red"
            ))
        except Exception as e:
            console.print(Panel(f"[danger]AN UNEXPECTED ERROR OCCURRED: {e}[/]",
                          title="[bold red]Error[/]", border_style="red"))

def main(input_file_path=None):
    """The main execution function for the e-book converter."""
    display_intro()
    
    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting E-book Converter[/]", border_style="green"))
            
    output_format_id = get_output_format()
    convert_ebook(input_file_path, output_format_id)

if __name__ == '__main__':
    main()
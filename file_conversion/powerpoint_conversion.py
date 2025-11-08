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
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "prompt": "bold yellow",
    "path": "bold cyan",
    "format": "bold blue",
})
console = Console(theme=custom_theme)


# --- DATA ENHANCEMENT: Detailed format descriptions ---
SUPPORTED_FORMATS = {
    # --- Presentation Formats (Editable) ---
    "PPTX": {"id": "pptx", "type": "[green]Editable Presentation[/]", "desc": "Modern Microsoft PowerPoint format. Best for compatibility."},
    "ODP": {"id": "odp", "type": "[green]Editable Presentation[/]", "desc": "OpenDocument format. Standard for LibreOffice/OpenOffice."},
    "PPT": {"id": "ppt", "type": "[yellow]Legacy Editable[/]", "desc": "Older PowerPoint format (97-2003). For compatibility with old software."},
    
    # --- Viewing & Sharing Formats (Not Editable) ---
    "PDF": {"id": "pdf", "type": "[blue]Fixed Document[/]", "desc": "Portable Document Format. Preserves layout perfectly for viewing/printing."},
    "PPSX": {"id": "ppsx", "type": "[blue]Slideshow[/]", "desc": "PowerPoint Show. Opens directly into presentation mode."},
    "PNG": {"id": "png", "type": "[cyan]Images[/]", "desc": "Exports [bold]each slide[/] as a separate high-quality PNG image file."},
}

def get_soffice_path():
    """Finds the path to the LibreOffice executable."""
    if sys.platform == "win32":
        paths = ["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe"]
        for path in paths:
            if os.path.exists(path): return path
    else:
        return shutil.which("soffice")
    return None

SOFFICE_PATH = get_soffice_path()

def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Presentation Converter 🐍[/]\n[cyan]A high-fidelity tool powered by the LibreOffice engine[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not SOFFICE_PATH:
        console.print(Panel(
            "[danger]CRITICAL: LibreOffice was not found on your system.[/]\n"
            "This script cannot function without a full LibreOffice installation.\n"
            "Please install it from [bold blue underline]https://www.libreoffice.org[/]",
            title="[bold red]Dependency Missing[/]", border_style="red"
        ))
        sys.exit(1)

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your presentation file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path):
            return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

def get_output_format():
    """RICH: Displays format options in a detailed table."""
    table = Table(title="[bold green]✅ Select an Output Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Type", style="white")
    table.add_column("Description", style="dim cyan")
    
    format_list = list(SUPPORTED_FORMATS.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['type'], details['desc'])
        
    console.print(table)
    
    choice = IntPrompt.ask(
        "[prompt]➡️  Enter the number for your choice[/prompt]",
        choices=[str(i) for i in range(1, len(format_list) + 1)]
    )
    return format_list[choice - 1][1]['id']

def convert_presentation(input_file_path, output_format):
    input_dir = os.path.dirname(input_file_path)
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    
    summary_panel = Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Output Format:[/info] [format]{output_format.upper()}[/]",
        title="[bold yellow]Conversion Summary[/]", border_style="yellow"
    )
    console.print(summary_panel)

    command = [
        SOFFICE_PATH, '--headless', '--convert-to', output_format,
        input_file_path, '--outdir', input_dir
    ]
    
    # RICH: Use console.status to provide feedback during the external process
    with console.status("[bold green]LibreOffice is processing your file in the background...", spinner="dots") as status:
        try:
            # Run the command, capturing output and checking for errors
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            # Determine the correct output path for the success message
            if output_format == 'png':
                final_path = f"Multiple PNG images in the folder: [path]{input_dir}[/]"
            else:
                output_file_name = f"{base_name}.{output_format}"
                final_path = os.path.join(input_dir, output_file_name)
            
            console.print(Panel(
                f"🎉 [success]Success! Conversion complete.[/] 🎉\n[info]Output saved at:[/info] [path]{final_path}[/]",
                title="[bold green]Complete[/]", border_style="green"
            ))

        except FileNotFoundError:
            console.print(Panel("[danger]CRITICAL ERROR: Could not find the LibreOffice executable.[/]\n"
                          "[warning]Please ensure LibreOffice is installed and its path is correct.[/]",
                          title="[bold red]Error[/]", border_style="red"))
        except subprocess.CalledProcessError as e:
            console.print(Panel(
                "[danger]LibreOffice failed to convert the file.[/]\n"
                "[warning]The input file may be corrupted, password-protected, or unsupported.[/]\n\n"
                f"[bold]Error Details from LibreOffice:[/]\n[dim]{e.stderr}[/dim]",
                title="[bold red]Conversion Failed[/]", border_style="red"
            ))
        except Exception as e:
            console.print(Panel(f"[danger]AN UNEXPECTED ERROR OCCURRED: {e}[/]",
                          title="[bold red]Error[/]", border_style="red"))


def main(input_file_path=None):
    """The main execution function for the presentation converter."""
    display_intro()

    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Presentation Converter[/]", border_style="green"))
            
    output_format_id = get_output_format()
    convert_presentation(input_file_path, output_format_id)

if __name__ == '__main__':
    main()
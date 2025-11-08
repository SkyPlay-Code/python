import os
import sys
import shutil
import tempfile

# RICH: Import necessary components
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.live import Live

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


def get_supported_formats():
    """
    Checks for available command-line tools and builds a detailed list of formats.
    """
    # --- DATA ENHANCEMENT: More detailed format descriptions ---
    base_formats = {
        "ZIP": {"id": "zip", "ext": ".zip", "comp": "[green]Good[/]", "desc": "Excellent compatibility for Windows, macOS, and Linux."},
        "TGZ": {"id": "gztar", "ext": ".tar.gz", "comp": "[green]Good[/]", "desc": "Standard for Linux/macOS. TAR archive compressed with GZip."},
        "TBZ2": {"id": "bztar", "ext": ".tar.bz2", "comp": "[blue]Better[/]", "desc": "TAR archive with BZip2 compression. Slower, but better ratio."},
        "TXZ": {"id": "xztar", "ext": ".tar.xz", "comp": "[blue]Excellent[/]", "desc": "TAR with XZ compression. Best ratio, modern Linux standard."},
        "TAR": {"id": "tar", "ext": ".tar", "comp": "[yellow]None[/]", "desc": "Combines files into one. No compression. Preserves permissions."},
    }
    
    # Dynamically add formats if their command-line tools are available
    if shutil.which('7z'):
        base_formats['7-ZIP'] = {"id": "7z", "ext": ".7z", "comp": "[blue]Excellent[/]", "desc": "High compression ratio via 7-Zip tool. [dim](Requires 7-Zip)[/]"}
        shutil.register_unpack_format("7z", [".7z"], lambda f, d: shutil.unpack_archive(f, d, format='7z'))
    
    if shutil.which('rar'):
        base_formats['RAR'] = {"id": "rar", "ext": ".rar", "comp": "[green]Good[/]", "desc": "Popular proprietary format. Good compression. [dim](Requires RAR)[/]"}
        shutil.register_unpack_format("rar", [".rar"], lambda f, d: shutil.unpack_archive(f, d, format='rar'))
        
    return base_formats

# We call this once at the start
SUPPORTED_FORMATS = get_supported_formats()


def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Archive Converter 🐍[/]\n[cyan]A simple tool to re-package compressed files using Python's shutil[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    # Check for missing dependencies and show a single panel if any are missing
    warnings = []
    if not shutil.which('7z'):
        warnings.append("[item]•[/] [bold]7-Zip[/] support is [danger]disabled[/]. ('7z' command not found)")
    if not shutil.which('rar'):
        warnings.append("[item]•[/] [bold]RAR[/] support is [danger]disabled[/]. ('rar' command not found)")

    if warnings:
        console.print(Panel(
            "\n".join(warnings),
            title="[warning]Optional Dependencies Missing[/]",
            border_style="yellow"
        ))

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your archive file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path):
            return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

def get_output_format():
    """RICH: Displays archive format options in a detailed table."""
    table = Table(title="[bold green]✅ Select an Output Archive Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Extension", style="magenta")
    table.add_column("Compression", style="white")
    table.add_column("Description", style="dim cyan")
    
    format_list = list(SUPPORTED_FORMATS.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['ext'], details['comp'], details['desc'])
        
    console.print(table)
    
    choice = IntPrompt.ask(
        "[prompt]➡️  Enter the number for your choice[/prompt]",
        choices=[str(i) for i in range(1, len(format_list) + 1)]
    )
    return format_list[choice - 1][1]['id']

def convert_archive(input_file_path, output_format):
    base_name = os.path.splitext(input_file_path)[0]
    output_archive_path_base = f"{base_name}_converted"
    temp_dir = tempfile.mkdtemp()

    final_archive_name = "" # To store the final filename

    # RICH: Use console.status to show the current step of the process
    with console.status("[bold green]Starting conversion...", spinner="dots") as status:
        try:
            # Step 1: Unpack
            status.update("[bold green]Step 1/3: Unpacking source archive to a temporary location...[/]")
            shutil.unpack_archive(input_file_path, temp_dir)
            
            # Step 2: Re-pack
            status.update(f"[bold green]Step 2/3: Creating new '{output_format.upper()}' archive...[/]")
            final_archive_name = shutil.make_archive(
                base_name=output_archive_path_base,
                format=output_format,
                root_dir=temp_dir
            )

            # Step 3: Clean up (will run in the 'finally' block)
            status.update("[bold green]Step 3/3: Cleaning up temporary files...[/]")

        except (shutil.ReadError, ValueError) as e:
            console.print(Panel(
                f"[danger]Could not read the input archive '[path]{os.path.basename(input_file_path)}[/]'.[/]\n"
                f"[warning]Reason:[/] {e}\n[dim]The file may be corrupted, password-protected, or in an unsupported format.[/]",
                title="[bold red]Critical Error[/]", border_style="red"
            ))
            final_archive_name = None # Flag as failed
        except Exception as e:
            console.print(Panel(f"[danger]AN UNEXPECTED ERROR OCCURRED: {e}[/]",
                          title="[bold red]Critical Error[/]", border_style="red"))
            final_archive_name = None # Flag as failed
        finally:
            shutil.rmtree(temp_dir)
            
    if final_archive_name:
        console.print(Panel(
            f"🎉 [success]Success! Conversion complete.[/] 🎉\n[info]New archive saved at:[/info] [path]{final_archive_name}[/]",
            title="[bold green]Complete[/]", border_style="green"
        ))

def main(input_file_path=None):
    """The main execution function for the archive converter."""
    display_intro()

    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Archive Converter[/]", border_style="green"))
            
    output_format_id = get_output_format()
    convert_archive(input_file_path, output_format_id)

if __name__ == '__main__':
    main()
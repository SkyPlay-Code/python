import os
import sys
import rawpy
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener

# RICH: Import the necessary components from the rich library
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.text import Text

# Enables Pillow to open HEIC/HEIF files (like iPhone photos)
register_heif_opener()

# RICH: Define a custom theme
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


# --- DATA ENHANCEMENT 1: Detailed format descriptions ---
SUPPORTED_FORMATS = {
    # --- Common Web & General Purpose Formats ---
    "JPEG": {"id": "jpeg", "type": "[orange3]Lossy[/]", "alpha": "No", "desc": "Best for photos on the web. Great compression."},
    "PNG": {"id": "png", "type": "[green]Lossless[/]", "alpha": "[bold green]Yes[/]", "desc": "Perfect for graphics, logos, and images needing transparency."},
    "WebP": {"id": "webp", "type": "[green]Both[/]", "alpha": "[bold green]Yes[/]", "desc": "Modern format for web. Excellent compression for both photos and graphics."},
    "GIF": {"id": "gif", "type": "[orange3]Lossy[/]", "alpha": "[bold green]Yes[/]", "desc": "Good for simple animations. Limited to 256 colors."},
    "BMP": {"id": "bmp", "type": "[green]Uncompressed[/]", "alpha": "No", "desc": "Simple, large, uncompressed format. Widely supported."},
    "TIFF": {"id": "tiff", "type": "[green]Lossless[/]", "alpha": "[bold green]Yes[/]", "desc": "High-quality format for print and archival purposes."},
    "HEIC": {"id": "heic", "type": "[orange3]Lossy[/]", "alpha": "[bold green]Yes[/]", "desc": "High Efficiency format used by modern iPhones. Great quality-to-size ratio."},
    
    # --- Professional & Specialized Formats ---
    "PSD": {"id": "psd", "type": "[blue]Layered[/]", "alpha": "[bold green]Yes[/]", "desc": "Adobe Photoshop's native format. Conversion will flatten the image."},
    "ICO": {"id": "ico", "type": "[green]Both[/]", "alpha": "[bold green]Yes[/]", "desc": "Standard format for website favicons and application icons."},
    "JP2": {"id": "jp2", "type": "[green]Both[/]", "alpha": "[bold green]Yes[/]", "desc": "JPEG 2000. Advanced compression, but less common than JPEG."},
}

RAW_EXTENSIONS = {'.dng', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.pef', '.raf', '.sr2', '.x3f', '.dcr'}


def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Image Converter 🐍[/]\n[cyan]A versatile tool for standard and RAW photos, powered by Pillow & Rich[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your image file[/prompt]").strip().replace("'", "").replace('"', '')
        if not os.path.exists(input_path):
            console.print("❌ [danger]ERROR: File not found. Please check the path and try again.[/]")
        elif not os.path.isfile(input_path):
            console.print(f"❌ [danger]ERROR: The path '[path]{input_path}[/]' is a directory, not a file.[/]")
        else:
            return input_path

def get_output_format():
    table = Table(title="[bold green]✅ Select an Output Image Format[/]", border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format", style="bold blue")
    table.add_column("Type", style="white")
    table.add_column("Supports Transparency?", justify="center")
    table.add_column("Best For", style="dim cyan")

    format_list = list(SUPPORTED_FORMATS.items())
    
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['type'], details['alpha'], details['desc'])
        
    console.print(table)
    
    while True:
        choice = IntPrompt.ask(
            "[prompt]➡️  Enter the number for your choice[/prompt]",
            choices=[str(i) for i in range(1, len(format_list) + 1)]
        )
        return format_list[choice - 1][1]['id'] # Return the format identifier

def get_quality_options(output_format):
    """RICH: Get quality options using styled, type-safe prompts."""
    options = {}
    if output_format.lower() in ['jpeg', 'jpg']:
        options['quality'] = IntPrompt.ask(
            "[prompt]➡️  Enter JPEG quality (1-100)[/prompt]", default=95,
            choices=[str(i) for i in range(1, 101)]
        )
    elif output_format.lower() == 'webp':
        options['quality'] = IntPrompt.ask(
            "[prompt]➡️  Enter WebP quality (1-100)[/prompt]", default=80,
            choices=[str(i) for i in range(1, 101)]
        )
    elif output_format.lower() == 'png':
        options['optimize'] = Confirm.ask(
            "[prompt]➡️  Enable PNG optimization? (Smaller file, longer save time)[/prompt]",
            default=False
        )
    return options

def convert_image(input_file_path, output_format, quality_options):
    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = f"{base_name}_converted.{output_format}"

    summary_panel = Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Output Format:[/info] [format]{output_format.upper()}[/]\n"
        f"[info]Output File:[/info] [path]{os.path.basename(output_file_path)}[/]",
        title="[bold yellow]Conversion Summary[/]", border_style="yellow"
    )
    console.print(summary_panel)

    try:
        image = None
        # RICH: Use a progress bar for a responsive feel
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            transient=True
        ) as progress:
            task = progress.add_task("[green]Processing...", total=100)
            
            # --- Step 1: Open the image ---
            file_ext = os.path.splitext(input_file_path)[1].lower()
            
            if file_ext in RAW_EXTENSIONS:
                progress.update(task, description="Decoding RAW file with rawpy...", advance=10)
                with rawpy.imread(input_file_path) as raw:
                    rgb_array = raw.postprocess()
                    image = Image.fromarray(rgb_array)
            else:
                progress.update(task, description="Opening image with Pillow...", advance=10)
                image = Image.open(input_file_path)
            
            progress.update(task, description="Image loaded.", advance=30)
            
            # --- Step 2: Handle Transparency ---
            alpha_format = next((v['alpha'] for k, v in SUPPORTED_FORMATS.items() if v['id'] == output_format), "No")
            if image.mode in ("RGBA", "LA", "P") and alpha_format == "No":
                progress.update(task, description="Flattening transparency...", advance=20)
                background = Image.new("RGB", image.size, (255, 255, 255))
                # Paste the image onto the background, using its alpha channel as a mask
                # Check for LA mode (Luminance + Alpha)
                if image.mode == 'LA':
                    image_rgba = image.convert('RGBA')
                    background.paste(image_rgba, mask=image_rgba.split()[3])
                else: # Assumes RGBA or P
                     # Ensure palette images are converted correctly before accessing split()
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[3])

                image = background
            
            # --- Step 3: Save the image ---
            progress.update(task, description="Saving new image file...", advance=30)
            image.save(output_file_path, format=output_format, **quality_options)
            progress.update(task, completed=100, description="Done!")

        console.print(Panel(
            f"🎉 [success]Success! Image conversion complete.[/] 🎉\n[info]New file saved at:[/info] [path]{output_file_path}[/]",
            title="[bold green]Complete[/]", border_style="green"
        ))

    except Exception as e:
        console.print(Panel(
            f"[danger]AN UNEXPECTED ERROR OCCURRED: {e}[/]\n"
            "[warning]The file may be corrupt, unsupported, or you may be missing a dependency (e.g., 'pillow-heif' for HEIC files).[/]",
            title="[bold red]Conversion Failed[/]", border_style="red"
        ))


def main(input_file_path=None):
    """The main execution function for the image converter."""
    display_intro()

    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Image Converter[/]", border_style="green"))

    output_format_id = get_output_format()
    options = get_quality_options(output_format_id)
    convert_image(input_file_path, output_format_id, options)

if __name__ == '__main__':
    main()
import os
import sys
import pypandoc
import fitz  # PyMuPDF

# RICH: Import necessary components
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

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

# Check for Pandoc installation
try:
    pypandoc.get_pandoc_version()
    PANDOC_INSTALLED = True
except OSError:
    PANDOC_INSTALLED = False

# --- DATA ENHANCEMENT: Detailed format descriptions ---
SUPPORTED_FORMATS = {
    # --- Formats Handled by Pandoc (Conversion Engine) ---
    "DOCX": {"id": "docx", "type": "[blue]Rich Text[/]", "desc": "Microsoft Word. Best for preserving complex layouts."},
    "ODT": {"id": "odt", "type": "[blue]Rich Text[/]", "desc": "OpenDocument format. Standard for LibreOffice/OpenOffice."},
    "HTML": {"id": "html", "type": "[green]Web[/]", "desc": "For display in web browsers. Will lose page-specific formatting."},
    "RTF": {"id": "rtf", "type": "[yellow]Legacy[/]", "desc": "Rich Text Format. Widely compatible with older word processors."},
    "TXT": {"id": "plain", "type": "[white]Plain Text[/]", "desc": "Removes all formatting, leaving only the text content."},
    "PDF": {"id": "pdf", "type": "[red]Fixed-Layout[/]", "desc": "[dim](Output Only)[/] Preserves visual appearance perfectly. [warning]Requires LaTeX engine.[/]"},
}

# Specific options for when the input is a fixed-layout format like PDF/XPS
PYMUPDF_OPTIONS = {
    "Extract Text to TXT": {"id": "txt_extract", "type": "[white]Text Data[/]", "desc": "Pulls all readable text from the document into a single .txt file."},
    "Pages to PNG Images": {"id": "png_pages", "type": "[cyan]Image Data[/]", "desc": "Creates a separate PNG image for each page of the document."},
}

PYMUPDF_INPUT_FORMATS = {'.pdf', '.xps', '.oxps', '.epub', '.cbz'}


def display_intro():
    console.print(Panel(
        "[bold green]🐍 Welcome to the Python Document Converter 🐍[/]\n[cyan]A powerful tool using Pandoc (for text) & PyMuPDF (for pages)[/]",
        title="[bold yellow]Converter[/]", border_style="green", padding=(1, 2)
    ))
    if not PANDOC_INSTALLED:
        console.print(Panel(
            "[warning]Pandoc is not found.[/warning]\nConversions between rich text formats (DOCX, ODT, etc.) will fail.\n"
            "Please install it from [bold blue underline]https://pandoc.org/installing.html[/]",
            title="[danger]Dependency Warning[/]", border_style="red"
        ))

def get_input_file():
    while True:
        input_path = Prompt.ask("\n[prompt]➡️  Enter the path to your document file[/prompt]").strip().replace("'", "").replace('"', '')
        if os.path.exists(input_path) and os.path.isfile(input_path):
            return input_path
        console.print("❌ [danger]ERROR: File not found or is not a valid file.[/]")

def get_output_format(is_special_input=False):
    """RICH: Displays format options in a detailed table."""
    options = PYMUPDF_OPTIONS if is_special_input else SUPPORTED_FORMATS
    title = ("[bold green]✅ Select an Output Option for your PDF/XPS File[/]"
             if is_special_input else "[bold green]✅ Select a Document Output Format[/]")
             
    table = Table(title=title, border_style="cyan", show_lines=True)
    table.add_column("Num", style="bold yellow", justify="center")
    table.add_column("Format / Option", style="bold blue")
    table.add_column("Type", style="white")
    table.add_column("Description", style="dim cyan")
    
    format_list = list(options.items())
    for i, (name, details) in enumerate(format_list, 1):
        table.add_row(str(i), name, details['type'], details['desc'])
        
    console.print(table)
    
    choice = IntPrompt.ask(
        "[prompt]➡️  Enter the number for your choice[/prompt]",
        choices=[str(i) for i in range(1, len(format_list) + 1)]
    )
    return format_list[choice - 1][1]['id']

def convert_with_pymupdf(input_path, output_format):
    base_name = os.path.splitext(input_path)[0]
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), transient=True) as progress:
        task = progress.add_task("[green]Processing...", total=1)
        doc = fitz.open(input_path)
        progress.update(task, total=len(doc)) # Set total to number of pages
        
        if output_format == "txt_extract":
            output_path = f"{base_name}_extracted.txt"
            with open(output_path, "w", encoding="utf-8") as txt_file:
                for page in doc:
                    txt_file.write(f"--- Page {page.number + 1} ---\n")
                    txt_file.write(page.get_text())
                    txt_file.write("\n\n")
                    progress.update(task, advance=1, description=f"Extracting text from page {page.number + 1}")
            return output_path
            
        elif output_format == "png_pages":
            output_dir = f"{base_name}_pages_as_images"
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            for page in doc:
                pix = page.get_pixmap()
                pix.save(os.path.join(output_dir, f"page_{page.number + 1}.png"))
                progress.update(task, advance=1, description=f"Saving page {page.number + 1} as PNG")
            return output_dir
    return None

def convert_with_pandoc(input_path, output_format):
    if not PANDOC_INSTALLED:
        console.print(Panel("[danger]Cannot convert: Pandoc is not installed on this system.[/]",
                      title="[bold red]Critical Error[/]", border_style="red"))
        return None
        
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}_converted.{output_format}"
    extra_args = ['--pdf-engine=xelatex'] if output_format == 'pdf' else []

    # RICH: Use a spinner for the conversion process
    with console.status("[bold green]Pandoc is converting your document...", spinner="dots"):
        try:
            pypandoc.convert_file(
                input_path,
                output_format,
                outputfile=output_path,
                extra_args=extra_args
            )
            return output_path
        except Exception as e:
            console.print(Panel(f"[danger]Pandoc conversion failed.[/]\n[bold]Details:[/bold]\n[dim]{e}[/dim]",
                          title="[bold red]Error[/]", border_style="red"))
            return None

def main(input_file_path=None):
    """The main execution function for the document converter."""
    display_intro()

    if not input_file_path:
        input_file_path = get_input_file()
    else:
        console.print(Panel(f"File provided: [path]{input_file_path}[/]",
            title="[bold green]Starting Document Converter[/]", border_style="green"))

    file_ext = os.path.splitext(input_file_path)[1].lower()
    is_special_format = file_ext in PYMUPDF_INPUT_FORMATS

    if is_special_format:
        console.print(Panel("[info]A PDF or fixed-layout file was detected.[/info]\n"
                      "Conversion options are focused on data extraction rather than reformatting.",
                      title="[bold cyan]Heads Up![/]", border_style="cyan"))

    output_format_id = get_output_format(is_special_input=is_special_format)
    
    console.print(Panel(
        f"[info]Input File:[/info] [path]{os.path.basename(input_file_path)}[/]\n"
        f"[info]Chosen Action:[/info] [format]{output_format_id.replace('_', ' ').title()}[/]",
        title="[bold yellow]Conversion Summary[/]", border_style="yellow"
    ))
    
    result_path = None
    if is_special_format:
        result_path = convert_with_pymupdf(input_file_path, output_format_id)
    else:
        result_path = convert_with_pandoc(input_file_path, output_format_id)

    if result_path:
        console.print(Panel(
            f"🎉 [success]Success! Conversion complete.[/] 🎉\n[info]Output saved at:[/info] [path]{result_path}[/]",
            title="[bold green]Complete[/]", border_style="green"
        ))
    else:
        console.print(Panel("[danger]Conversion Failed.[/]\nPlease review any error messages above.",
                      title="[bold red]Failed[/]", border_style="red"))

if __name__ == '__main__':
    main()
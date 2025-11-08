import os
import subprocess
import json
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from art import tprint

def typing_effect(console, text, speed=0.01):
    """Creates a typewriter effect for the given text using the rich console."""
    for char in text:
        console.print(char, end="")
        sys.stdout.flush()
        time.sleep(speed)
    console.print()

def execute_ai_plan():
    """
    More advanced AI automation script that uses a structured JSON response
    to decide file types and actions autonomously.
    """
    console = Console()

    # --- Stylized Welcome ---
    console.clear()
    tprint("A.I.  CORE", font="doh")
    console.print(Panel.fit("[bold green]AUTONOMOUS EXECUTION PROTOCOL ENGAGED[/bold green]", border_style="green"))
    console.print()

    # Attempt to load the Gemini client
    try:
        from google import genai
        from google.genai import types

        api_key = "GEMINI_API_KEY"
        if not api_key:
            console.print("[bold red]ERROR: GEMINI_API_KEY environment variable not found.[/bold red]")
            return
        
        client = genai.Client(api_key=api_key)
        model = "gemini-2.5-pro" # Using a powerful model for better JSON compliance
    except ImportError:
        console.print("[bold red]ERROR: The 'google-genai' library is not installed. Please run 'pip install google-genai'.[/bold red]")
        return
    except Exception as e:
        console.print(f"[bold red]An error occurred during client initialization: {e}[/bold red]")
        return


    while True:
        try:
            user_command = console.input("[bold cyan]A.I. Core > [/bold cyan]")
            if user_command.lower() in ['exit', 'quit']:
                typing_effect(console, "\n[bold yellow]Shutting down A.I. Core...[/bold yellow]")
                break

            with console.status("[bold yellow]Delegating task to AI model...[/bold yellow]", spinner="dots"):
                # --- This is the new, more intelligent prompt ---
                prompt = f"""
                You are an expert-level programmer and system automator. Your task is to convert a natural language command into a structured JSON object that a Python script can execute.

                The JSON object must have the following structure:
                {{
                  "language": "language_name",
                  "filename": "suggested_filename.ext",
                  "code": "code_to_be_written",
                  "action": "action_to_perform"
                }}

                - `language`: The programming language (e.g., "python", "html", "javascript", "css", "shell").
                - `filename`: A logical filename with the correct extension. Use "none" if no file is needed (e.g., for a direct shell command).
                - `code`: The complete, raw code.
                - `action`: The final step for the execution script. Must be one of:
                  - "execute": For running scripts (python, nodejs, shell).
                  - "open": For opening files in a default application (html, txt, jpg).
                  - "none": If only saving the file is required (css, json config).

                User Command: "{user_command}"

                Respond with ONLY the raw JSON object and nothing else.
                """

                contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
                
                response_text = ""
                for chunk in client.models.generate_content_stream(model=model, contents=contents):
                    response_text += chunk.text

            # --- Parsing and Execution Logic ---
            typing_effect(console, "[bold green]...Plan received from AI. Decoding...[/bold green]")
            
            # Clean the response to ensure it's valid JSON
            clean_response = response_text.strip().replace("```json", "").replace("```", "")
            
            try:
                plan = json.loads(clean_response)
            except json.JSONDecodeError:
                console.print("[bold red]Error: AI did not return a valid JSON plan. Unable to proceed.[/bold red]")
                console.print("--- RAW AI RESPONSE ---")
                console.print(response_text)
                console.print("----------------------")
                continue

            # Display the AI's plan in a readable format
            console.print(Panel(f"[bold]Language:[/bold] {plan['language']}\n[bold]Filename:[/bold] {plan['filename']}\n[bold]Action:[/bold] {plan['action']}",
                                title="[yellow]Execution Plan[/yellow]", border_style="yellow"))

            console.print(Syntax(plan['code'], plan['language'], theme="monokai", line_numbers=True))
            
            filename = plan.get("filename")
            code = plan.get("code")
            action = plan.get("action")
            language = plan.get("language")

            # Save the file if a filename is provided
            if filename and filename != "none":
                with open(filename, "w") as f:
                    f.write(code)
                console.print(f"\n[green]Successfully saved code to [bold cyan]{filename}[/bold cyan][/green]")

            # Perform the specified action
            if action == "execute":
                typing_effect(console, f"[yellow]Executing [bold]{filename or 'command'}[/bold]...[/yellow]")
                try:
                    if language == "python":
                        subprocess.run(["python", filename], check=True)
                    elif language == "javascript":
                        # Assumes Node.js is installed
                        subprocess.run(["node", filename], check=True)
                    elif language == "shell":
                        subprocess.run(code, shell=True, check=True)
                    console.print("[bold green]Execution successful.[/bold green]")
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    console.print(f"[bold red]Execution failed: {e}[/bold red]")

            elif action == "open":
                typing_effect(console, f"[yellow]Opening [bold]{filename}[/bold]...[/yellow]")
                try:
                    if sys.platform == "win32":
                        os.startfile(filename)
                    elif sys.platform == "darwin": # macOS
                        subprocess.run(["open", filename], check=True)
                    else: # linux
                        subprocess.run(["xdg-open", filename], check=True)
                    console.print("[bold green]File opened.[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]Failed to open file: {e}[/bold red]")
            
            elif action == "none":
                console.print("[yellow]Action is 'none'. Task complete.[/yellow]")

        except Exception as e:
            console.print(f"\n[bold red]A critical error occurred in the main loop: {e}[/bold red]")

        console.print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    execute_ai_plan()
from rich.console import Console
from rich.panel import Panel
import questionary
from questionary import Style

import sys
import platform
import os

from typing import List
from functools import wraps

class CLI:

    CONSOLE = Console()

    SELECT_DEFAULT_STYLE: Style = Style([
        ("question", "bold"),            
        ("answer", "fg:#047F80 bold"),      
        ("pointer", "fg:#047F80 bold"),      
        ("highlighted", "fg:#047F80 bold"),
        ("selected", "fg:#047F80 bold"),  
    ])
    ASK_DEFAULT_STYLE: Style = Style([
        ("question", "bold"), 
        ("answer", "fg:#047F80"),          
    ])

    PREFIX: str = f"{os.getcwd()} >>>"

    @staticmethod
    def ask(prompt: str, style: Style | None = None, type: str = "text", prefixed: bool = True, check: bool = True, validate = lambda text: True):

        if type == "text":
            result = questionary.text(f"{CLI.PREFIX if prefixed else ""}{prompt}", style=style if style else Style([("question", "bold"), ("answer", "#ffffff")]), validate=validate).ask()
        else:
            result = questionary.confirm(f"{CLI.PREFIX if prefixed else ""}{prompt}", style=style if style else Style([("question", "bold"), ("answer", "#ffffff")]), default=True).ask()

        if result is None:
            sys.exit(0)

        if check:
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")

            color = "#ffffff"
            if style:
                for selector, rule in style.style_rules:
                    if selector == "answer":
                        color = rule[rule.find("#"):]

            if type == "text":
                CLI.CONSOLE.print(f"{CLI.PREFIX if prefixed else ""}" + f"[green]✔[/green] [bold]{prompt}[/bold] [{color} bold]{result}[/{color} bold]")
            else:
                CLI.CONSOLE.print(f"{CLI.PREFIX if prefixed else ""}" + f"[green]✔[/green] [bold]{prompt}[/bold] [{color} bold]{"Y" if result else "N"}[/{color} bold]")

        return result
    
    @staticmethod
    def create_config():

        CLI.CONSOLE.print("\n")
        CLI.CONSOLE.print(
            Panel.fit(
                "[bold white on black] ✨ simplr ✨[/bold white on black]\n"
                "[dim] Please complete the configuration steps before continuing.\n See https://github.com/noahl25/simplr for more information. [/dim]",
                border_style="cyan",
                padding=(1, 3),
                title="[cyan] Welcome![/cyan]",
                subtitle="v0.0.1"
            )
        )
        
        google_api_key = CLI.ask("Enter your Google Gemini API key:", style=CLI.ASK_DEFAULT_STYLE, prefixed=False)
        cache_chats = CLI.ask("Cache previous chats? (Recommended)", style=CLI.ASK_DEFAULT_STYLE, type="confirm", prefixed=False)
        max_search_depth = CLI.ask("Search depth for file structure? (1 Recommended for low token limits)", style=CLI.ASK_DEFAULT_STYLE, prefixed=False, validate=lambda text: text.isdigit())

        CLI.CONSOLE.print("\nEnter the simplr CLI anytime with [bold #047F80]simplr run[/bold #047F80].")
        CLI.CONSOLE.print("[dim]Ask LLM in a single command with [#047F80]simplr \"REQUEST\"[/#047F80].[/dim]")
        CLI.CONSOLE.print("[dim]Redo your config anytime with [#047F80]simplr config[/#047F80].[/dim]")

        return {
            "google_api_key": google_api_key,
            "cache_chats": cache_chats,
            "max_search_depth": int(max_search_depth),
            "platform": platform.system()
        }

    @staticmethod
    def select(prompt: str, choices: List[str], style: Style | None = None, prefixed: bool = True):
        result = questionary.select(
            f"{CLI.PREFIX if prefixed else ""}{prompt}",
            choices=choices,
            style=style if style else Style([("question", "bold"), ("answer", "#ffffff")])
        ).ask()
        return result
    
from rich.console import Console
from rich.text import Text
from pyfiglet import Figlet
from rich.panel import Panel

def display_banner(title: str):
    console = Console()
    fig = Figlet(font='slant', width=80)
    banner_text = fig.renderText(title)

    styled_text = Text(banner_text, style="bold magenta")
    styled_text.stylize("bold magenta", 0, len(banner_text)//3)
    styled_text.stylize("bold blue", len(banner_text)//3, 2*len(banner_text)//3)
    styled_text.stylize("bold cyan", 2*len(banner_text)//3, len(banner_text))
    console.print(styled_text, justify="center")
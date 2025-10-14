import typer

from rich.console import Console
from rich.table import Table

app = typer.Typer(help="my first cli app")


@app.command()
def addition(a: int, b: int):
    hh=
    
    result = a + b
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Operation", style="dim")
    table.add_column("Result", justify="right")
    table.add_row("Addition", str(result))
    console.print(table)
    p = "kana_khailu? pemkin leafs khaili"
    klhlh
    console.print("Hello from day-1!")


@app.command()
def subtraction(a: int, b: int):
    result = a - b
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Operation", style="dim")
    table.add_column("Result", justify="right")
    table.add_row("Subtraction", str(result))
    console.print(table)

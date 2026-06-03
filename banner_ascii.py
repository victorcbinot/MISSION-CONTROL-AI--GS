"""
banner_ascii.py — Gerador standalone de banner ASCII art.
Útil para testar fontes e customizar o banner do projeto.

Uso:
    python banner_ascii.py
    python banner_ascii.py -fonts
    python banner_ascii.py -font slant -text "EnviroSat"
    python banner_ascii.py -demo
"""

import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text

console = Console()


def banner_padrao():
    linha1 = pyfiglet.figlet_format("Global Solution", font="ansi_shadow")
    linha2 = pyfiglet.figlet_format("Mission Control AI", font="ansi_shadow")
    console.print(Align.center(Text(linha1, style="bold #A855F7")))
    console.print(Align.center(Text(linha2, style="bold #06B6D4")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP ──",
             style="italic #8484A0")
    ))


def listar_fontes():
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(f"[bold cyan]{len(fontes)} fontes disponíveis:[/bold cyan]")
    for f in sorted(fontes):
        console.print(f"  {f}")


def testar_fonte(font: str, text: str):
    try:
        resultado = pyfiglet.figlet_format(text, font=font)
        console.print(Text(resultado, style="bold #06B6D4"))
    except pyfiglet.FontNotFound:
        console.print(f"[red]Fonte '{font}' não encontrada.[/red]")


def demo():
    fontes_demo = ["ansi_shadow", "slant", "small", "banner3", "doom", "big", "block", "digital"]
    texto = "EnviroSat"
    for fonte in fontes_demo:
        console.rule(f"[dim]{fonte}[/dim]")
        try:
            console.print(Text(pyfiglet.figlet_format(texto, font=fonte), style="bold green"))
        except Exception:
            console.print(f"[dim]Fonte {fonte} indisponível[/dim]")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        banner_padrao()
    elif "-fonts" in args:
        listar_fontes()
    elif "-demo" in args:
        demo()
    elif "-font" in args and "-text" in args:
        idx_font = args.index("-font")
        idx_text = args.index("-text")
        testar_fonte(args[idx_font + 1], args[idx_text + 1])
    elif "-font" in args:
        idx_font = args.index("-font")
        testar_fonte(args[idx_font + 1], "Mission Control AI")
    else:
        banner_padrao()
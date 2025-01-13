import re
from termcolor import colored
import sys

def log(msg, color="blue"):
    print(colored("(*)", color, attrs=["bold"], force_color=True) + f" {msg}")


def command(msg, color="yellow"):
    print(colored(" > ", color, attrs=["bold"], force_color=True) + f" {msg}")


def error(msg, color="red"):
    print(colored(" ! ", color, attrs=["bold"], force_color=True) + f" {msg}")


def result(msg, color="magenta"):
    print(colored(" ~ ", color, attrs=["bold"], force_color=True) + f"{msg}")


def list_obj(index: int, msg: str, color="yellow"):
    print(f"{' '*3} {colored(f'{index}.', color, attrs=['bold'], force_color=True)} {msg}")


def bold(text: str, color: str):
    return colored(text, color=color, attrs=["bold"], force_color=True)


def subscript_number(n: int) -> str:
    s = ""
    subscripts = "₀₁₂₃₄₅₆₇₈₉"
    while n:
        (n, d) = divmod(n, 10)
        s = subscripts[d] + s
    return s


def plain(s: str) -> str:
    ae = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ae.sub("", s)

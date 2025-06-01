import re
import sys
from typing import List

import click
from colorama import Fore, Style


def visible_length(s):
    # Strip ANSI color codes
    return len(re.sub(r'\x1b\[[0-9;]*m', '', s))


def _get_box_chars():
    try:
        '┌'.encode(sys.stdout.encoding)
        return '┌', '┐', '└', '┘', '─', '│'
    except UnicodeEncodeError:
        return '+', '+', '+', '+', '-', '|'


def print_boxed_message(message, color=Fore.BLUE, text_color=Fore.YELLOW):
    click.echo('')
    lines = message.split('\n')
    width = max(visible_length(line) for line in lines)
    # +2 for single space padding left and right of each line
    box_width = width + 2

    tl, tr, bl, br, hor, ver = _get_box_chars()
    click.echo(color + tl + (hor * box_width) + tr)
    for line in lines:
        vis_len = visible_length(line)
        pad_right = ' ' * (width - vis_len)
        click.echo(color + ver + Style.RESET_ALL + ' ' + text_color + line + Style.RESET_ALL + pad_right + ' ' + color + ver)
    click.echo(color + bl + (hor * box_width) + br + Style.RESET_ALL)
    click.echo('')


def print_list(title: str, items: List, title_color=Fore.CYAN, items_color=Fore.YELLOW, tab_size: int = 2, add_empty_line: bool = True):
    print(f'{title_color}{title}{Fore.RESET}:')
    indent = ' ' * tab_size
    for item in items:
        print(f'{items_color}{indent}- {item}{Fore.RESET}')

    if add_empty_line:
        print('')

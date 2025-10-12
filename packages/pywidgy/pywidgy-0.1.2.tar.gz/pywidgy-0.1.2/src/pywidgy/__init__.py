from .checkboxes import Checkboxes
from .dialog import Dialog
from .free_text import FreeText
from .menu import Menu, MenuItem
from .runner import run_stack
from .table import Table
from .widget import WidgetStack

_STACK = None


def init():
    global _STACK  # pylint: disable=global-statement
    if _STACK is None:
        _STACK = WidgetStack()
    else:
        raise RuntimeError("pywidgy.init() has already been called")


def run():
    run_stack(_STACK)


def spawn(widget):
    _STACK.push(widget)


def close():
    _STACK.pop()


__all__ = [
    "Checkboxes",
    "Dialog",
    "FreeText",
    "Menu",
    "MenuItem",
    "Table",
]

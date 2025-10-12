from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class MenuItem:
    label: str
    callback: Callable[[], None]


class Menu:

    def __init__(
        self,
        title: str,
        items: list[MenuItem],
        exit_cb: Optional[Callable[[], None]] = None,
    ):
        self.title = title
        self.items = items
        self.selected_row = 0
        self.exit_cb = exit_cb

    @property
    def selected(self) -> MenuItem:
        return self.items[self.selected_row]

    def handle_key(self, key):
        if key.name == "KEY_UP":
            self.selected_row = (self.selected_row - 1) % len(self.items)
        elif key.name in ("KEY_ESCAPE",) or key.lower() == "q":
            if self.exit_cb:
                self.exit_cb()
        elif key.name in ("KEY_ENTER", "\n"):
            self.items[self.selected_row].callback()
        elif key.name == "KEY_DOWN":
            self.selected_row = (self.selected_row + 1) % len(self.items)

    def draw(self, term, pos=(0, 0)):
        x, y = pos
        inner_width = max(
            len(s) for s in ([self.title] + [i.label for i in self.items])
        )
        print(term.move_xy(x, y) + "┌" + "─" * inner_width + "┐")
        print(term.move_xy(x, y + 1) + "│" + self.title.ljust(inner_width) + "│")
        print(term.move_xy(x, y + 2) + "│" + "-" * (inner_width) + "│")
        for i, item in enumerate(self.items):
            line = term.reverse(item.label) if i == self.selected_row else item.label
            print(
                term.move_xy(x, y + i + 3)
                + "│"
                + line
                + " " * (inner_width - len(item.label))
                + "│"
            )
        print(
            term.move_xy(x, y + len(self.items) + 2 + 1) + "└" + "─" * inner_width + "┘"
        )

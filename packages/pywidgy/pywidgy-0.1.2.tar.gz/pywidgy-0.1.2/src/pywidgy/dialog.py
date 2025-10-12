from typing import Callable, Optional

from .menu import MenuItem


class Dialog:
    def __init__(
        self,
        question: str,
        items: list[MenuItem],
        exit_cb: Optional[Callable[[], None]] = None,
    ):
        self.question = question
        self.items = items
        self.selected_row = 0
        self.exit_cb = exit_cb

    @property
    def selected(self) -> MenuItem:
        return self.items[self.selected_row]

    def draw(self, term, pos=(0, 0)):
        x, y = pos
        inner_width = max(
            len(self.question), len(" ".join([s.label for s in self.items]))
        )
        options_line = ""
        for i, opt in enumerate(self.items):
            if i == self.selected_row:
                options_line += term.reverse(f"{opt.label} ")
            else:
                options_line += f"{opt.label} "
        print(term.move_xy(x, y) + "┌" + "─" * inner_width + "┐")
        print(term.move_xy(x, y + 1) + "│" + self.question.ljust(inner_width) + "│")
        print(
            term.move_xy(x, y + 2)
            + "│"
            + options_line
            + " " * (inner_width - len(" ".join([s.label for s in self.items])) - 1)
            + "│"
        )
        print(term.move_xy(x, y + 3) + "└" + "─" * inner_width + "┘")

    def handle_key(self, key):
        if key.name == "KEY_LEFT":
            self.selected_row = (self.selected_row - 1) % len(self.items)
        elif key.name == "KEY_RIGHT":
            self.selected_row = (self.selected_row + 1) % len(self.items)
        elif key.name in ("KEY_ENTER", "\n"):
            self.items[self.selected_row].callback()
        elif key.name in ("KEY_ESCAPE",) or key.lower() == "q":
            if self.exit_cb:
                self.exit_cb()

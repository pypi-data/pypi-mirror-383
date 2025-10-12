from dataclasses import fields
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Table(Generic[T]):
    def __init__(
        self,
        items: list[T],
        column_widths: list[int],
        on_enter_cb: Callable[[T], None],
        exit_cb: Optional[Callable[[], None]] = None,
    ):
        self.items = items
        self.on_enter_cb = on_enter_cb
        self.exit_cb = exit_cb
        self.selected_row = 0
        self.column_widths = column_widths
        self.column_headers = [f.name for f in fields(items[0])]  # type: ignore[arg-type] # noqa: E501

    @property
    def selected(self) -> T:
        return self.items[self.selected_row]

    def format_row(self, row):
        return "|".join(
            str(cell).ljust(w)[:w] for cell, w in zip(row, self.column_widths)
        )

    def handle_key(self, key):
        if key.name == "KEY_UP":
            self.selected_row = (self.selected_row - 1) % len(self.items)
        elif key.name == "KEY_DOWN":
            self.selected_row = (self.selected_row + 1) % len(self.items)
        elif key.name in ("KEY_ENTER", "\n"):
            self.on_enter_cb(self.selected)
        elif key.lower() == "q":
            if self.exit_cb:
                self.exit_cb()

    def draw(self, term, pos=(0, 0)):
        x, y = pos
        print(
            term.move_xy(x, y)
            + self.format_row(list(map(str.capitalize, self.column_headers)))
        )
        print(term.move_xy(x, y + 1) + "+".join("-" * w for w in self.column_widths))
        for i, item in enumerate(self.items):
            row_y = y + 2 + i
            line = self.format_row([getattr(item, f) for f in self.column_headers])
            print(
                term.move_xy(x, row_y)
                + (term.reverse(line) if i == self.selected_row else line)
            )
        footer_y = y + 2 + len(self.items) + 1
        print(term.move_xy(x, footer_y) + "↑/↓ move • ENTER menu • q quit")

from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Checkboxes(Generic[T]):
    def __init__(
        self,
        title: str,
        options: list[T],
        size: tuple[int, int],
        exit_cb: Optional[Callable[[T], None]] = None,
    ):
        self.title = title
        self.options: list[T] = options
        self.exit_cb = exit_cb
        self.size = size
        self.curr_row = 0
        self.selected_rows: list[int] = []

    @property
    def selected(self) -> list[T]:
        return [self.options[i] for i in self.selected_rows]

    def handle_key(self, key):
        if key.name == "KEY_UP":
            self.curr_row = (self.curr_row - 1) % len(self.options)
        elif key.name == "KEY_DOWN":
            self.curr_row = (self.curr_row + 1) % len(self.options)
        elif key == " ":
            if self.curr_row in self.selected_rows:
                self.selected_rows.remove(self.curr_row)
            else:
                self.selected_rows.append(self.curr_row)
        elif key.lower() == "q":
            if self.exit_cb:
                self.exit_cb(self.selected)

    def draw(self, term, pos=(0, 0)):
        x, y = pos
        inner_width = max(
            len(s) for s in ([self.title] + [f"{i}" for i in self.options])
        )
        print(term.move_xy(x, y) + "┌" + "─" * inner_width + "┐")
        print(term.move_xy(x, y + 1) + "│" + self.title.ljust(inner_width) + "│")
        print(term.move_xy(x, y + 2) + "│" + "-" * (inner_width) + "│")
        for i, item in enumerate(self._get_options_with_boxes()):
            line = term.reverse(item) if i == self.curr_row else item
            print(
                term.move_xy(x, y + i + 3)
                + "│"
                + line
                + " " * (inner_width - len(item))
                + "│"
            )
        print(
            term.move_xy(x, y + len(self.options) + 2 + 1)
            + "└"
            + "─" * inner_width
            + "┘"
        )

    def _get_options_with_boxes(self) -> list[str]:
        result = []
        for i, option in enumerate(self.options):
            box = "[X]" if i in self.selected_rows else "[ ]"
            result.append(" ".join([box, str(option)]))
        return result


#        print(term.move_xy(x, footer_y) + "↑/↓ move • ENTER menu • q quit")

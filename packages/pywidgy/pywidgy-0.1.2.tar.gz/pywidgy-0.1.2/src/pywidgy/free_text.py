from typing import Callable, Optional


class FreeText:
    def __init__(
        self,
        lines: list[str],
        size: tuple[int, int],
        exit_cb: Optional[Callable[[], None]] = None,
    ):
        self.lines = lines
        self.exit_cb = exit_cb
        self.size = size
        self.scroll = (0, 0)

    def draw(self, term, pos=(0, 0)):
        x, y = pos
        visible = self._scroll_text(self.scroll[0], self.scroll[1])
        print(term.move_xy(x, y) + "┌" + "─" * self.size[0] + "┐")
        for n in range(self.size[1]):
            if n < len(visible):
                print(
                    term.move_xy(x, y + n + 1)
                    + "│"
                    + visible[n]
                    + " " * (self.size[0] - len(visible[n]))
                    + "│"
                )
            else:
                print(term.move_xy(x, y + n + 1) + "│" + " " * self.size[0] + "│")
        print(term.move_xy(x, y + n + 1) + "└" + "─" * self.size[0] + "┘")
        #: 42% vertical, 10% horizontal (↑↓ ←→ to scroll)

    def handle_key(self, key):
        scroll_x = self.scroll[0]
        scroll_y = self.scroll[1]
        if key.name == "KEY_UP":
            scroll_y = self.scroll[1] - 1 if self.scroll[1] > 0 else 0
        elif key.name == "KEY_DOWN":
            scroll_y += 1
            if len(self._scroll_text(scroll_x, scroll_y)) < self.size[1]:
                scroll_y = self.scroll[1]
        elif key.name == "KEY_LEFT":
            scroll_x = self.scroll[0] - 1 if self.scroll[0] > 0 else 0
        elif key.name == "KEY_RIGHT":
            if (longest_line := max(len(s) for s in self.lines)) > self.size[0]:
                max_x_scroll = longest_line - self.size[0]
                scroll_x += 1
                if scroll_x == max_x_scroll:
                    scroll_x = self.scroll[0]
        if key.name in ("KEY_ESCAPE", "q") or key.lower() == "q":
            if self.exit_cb:
                self.exit_cb()
        self.scroll = (scroll_x, scroll_y)

    def _scroll_text(self, horizontal: int, vertical: int):
        return [
            line[horizontal : horizontal + self.size[0]]
            for line in self.lines[vertical : vertical + self.size[1]]
        ]

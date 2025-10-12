from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class StackItem:
    widget: Any
    position: tuple[int, int]


class WidgetStack:

    def __init__(self) -> None:
        self.stack: list[StackItem] = []

    def push(self, widget, pos=(0, 0)) -> None:
        child_pos = pos
        if parent_widget := self.top():
            parent_x, parent_y = parent_widget.position
            child_pos = (pos[0] + parent_x, pos[1] + parent_y)
        self.stack.append(StackItem(widget=widget, position=child_pos))

    def pop(self) -> Optional[StackItem]:
        if self.stack:
            return self.stack.pop()
        return None

    def top(self) -> Optional[StackItem]:
        if self.stack:
            return self.stack[-1]
        return None

    def handle_key(self, key):
        item = self.top()
        if widget := item.widget:
            widget.handle_key(key)

    def draw(self, term):
        print(term.clear)
        for item in self.stack:
            item.widget.draw(term, item.position)

    def __len__(self):
        return len(self.stack)

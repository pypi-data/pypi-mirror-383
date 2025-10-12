from blessed import Terminal

from .widget import WidgetStack


def run_stack(stack: WidgetStack):
    term = Terminal()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.clear)
            stack.draw(term)
            key = term.inkey(timeout=0.5)
            stack.handle_key(key)
            if len(stack) == 0:
                break
    print()

from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, RichLog
from textual.widget import Widget
from rich.text import Text

class LogTab(Widget):
    def compose(self) -> ComposeResult:
        # Key: wrap=True; we'll write Text(overflow="fold")
        self.r_log = RichLog(wrap=True, markup=False, auto_scroll=False)
        yield self.r_log

    def on_mount(self) -> None:
        # Extremely long tokens to test wrapping
        long_a = "diff --git a/" + "x"*200 + " b/" + "y"*200
        long_b = "+" + "A"*300
        self.r_log.write(Text(long_a, overflow="fold"))
        self.r_log.write(Text(long_b, style="green", overflow="fold"))
        self.r_log.write(Text("normal words should wrap too", overflow="fold"))

class Demo(App):
    CSS = """
    TabPane { layout: vertical; padding: 1; }
    RichLog { width: 100%; height: 1fr; overflow-x: hidden; }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Diff"):
                yield LogTab()

if __name__ == "__main__":
    Demo().run()


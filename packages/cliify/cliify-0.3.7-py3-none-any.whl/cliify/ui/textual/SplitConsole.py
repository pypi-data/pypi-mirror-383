try:
    from textual.app import App, ComposeResult
    from textual.containers import Container
    from textual.widgets import Static, Input, RichLog, Header, Footer
    from textual.reactive import reactive
    from textual.binding import Binding
    from textual_autocomplete import AutoComplete, DropdownItem
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from typing import Optional, Any, Callable
import builtins

from cliify.ui.LogRouter import configure_logging
from cliify.completers.textual import CommandCompleter

import logging 

logger = logging.getLogger("SplitConsole")

if TEXTUAL_AVAILABLE:
    class CommandInput(Input):
        """Custom Input widget with history support"""
        
        def __init__(self, session: Any, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.session = session
            self.history = []
            self.history_index = -1
            self.current_input = ""
                
        def add_to_history(self, command: str):
            """Add command to history"""
            if command and (not self.history or self.history[-1] != command):
                self.history.append(command)
            self.history_index = -1
            
        async def key_up(self) -> None:
            """Handle up arrow - previous command in history"""
            if not self.history:
                return
                
            if self.history_index == -1:
                self.current_input = self.value
                self.history_index = len(self.history) - 1
            elif self.history_index > 0:
                self.history_index -= 1
                
            if 0 <= self.history_index < len(self.history):
                self.value = self.history[self.history_index]
                self.cursor_position = len(self.value)
                
        async def key_down(self) -> None:
            """Handle down arrow - next command in history"""
            if not self.history or self.history_index == -1:
                return
                
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.value = self.history[self.history_index]
            else:
                self.history_index = -1
                self.value = self.current_input
                
            self.cursor_position = len(self.value)

    class CommandAutoComplete(AutoComplete):
        def __init__(self, input_widget: CommandInput, session: Any):
            super().__init__(input_widget, candidates=None)
            self.session = session

        def get_candidates(self, value: str) -> list[DropdownItem]:
            """Get completion candidates"""
            try:
                if not hasattr(self.session, 'getCompletions'):
                    return []
                
                completions = self.session.getCompletions(value)
                if not completions:
                    return []
                
                # Filter out special markers and create dropdown items
                items = []
                for comp in completions:
                    comp_str = str(comp).strip()
                    if comp_str.startswith("!"):
                        continue
                    if comp_str in ["$file", "$commands"]:
                        continue
                    items.append(DropdownItem(main=comp_str))
                
                return items[:10]  # Limit to 10 items
            except Exception:
                return []

    class SplitConsole(App):
        CSS = """
        Screen {
            layout: vertical;
        }
        
        .banner {
            height: 1;
            background: $surface;
            color: $primary;
            padding: 0 1;
        }
        
        .output-container {
            height: 1fr;
            border: none;
        }
        
        .input-container {
            height: 1;
            border: none;
            padding: 0;
        }
        
        Input {
            height: 1;
            width: 1fr;
            margin: 0;
            padding: 0;
            border: none;
        }
        
        RichLog {
            height: 1fr;
            scrollbar-gutter: stable;
        }
        """

        BINDINGS = [
            Binding("ctrl+c", "quit", "Quit", show=False),
        ]

        status_text = reactive("")
        banner_text = reactive("")

        def __init__(self, 
                     session: Any,      
                     bannerText: str,
                     historyFile: Optional[str] = None,
                     routePrint: bool = True,
                     routeLogs: bool = True,
                     routeStdout: bool = True,
                     routeStderr: bool = True,
                     logLevel: str = "INFO",
                     exitCallback: Optional[Callable] = None,
                     title: Optional[str] = None
                     ):
            super().__init__()
            self.session = session
            self.banner_text = bannerText
            self.exitCallback = exitCallback
            
            if title:
                self.title = title
            else:
                self.title = "Textual Split Console"

            # Route print and logs
            if routePrint:
                builtins.print = self.print_redirect

            if routeLogs:
                configure_logging(self.print_ansi, logLevel)

        def compose(self) -> ComposeResult:
            """Create the layout"""
            yield Header()
            
            with Container(classes="banner"):
                yield Static(self.banner_text, id="banner-text")
                yield Static(self.status_text, id="status-text")
            
            with Container(classes="output-container"):
                yield RichLog(id="output", markup=True, highlight=True, auto_scroll=True)
            
            with Container(classes="input-container"):
                input_widget = CommandInput(
                    self.session,
                    placeholder="Enter command...",
                    id="command-input"
                )
                yield input_widget
                yield CommandAutoComplete(input_widget, self.session)
                
            yield Footer()

        def on_mount(self) -> None:
            """Initialize the console when mounted"""
            self.query_one("#command-input", Input).focus()

        async def on_input_submitted(self, event: Input.Submitted) -> None:
            """Handle command submission"""
            line = event.value.strip()
            if not line:
                self.print_ansi("")
                return
            
            # Add to history if it's a CommandInput
            if isinstance(event.input, CommandInput):
                event.input.add_to_history(line)
                
            # Clear the input
            event.input.value = ""
            
            # Execute the command
            if hasattr(self.session, 'parseCommand'):
                try:
                    self.session.parseCommand(line)
                except Exception as e:
                    logger.error(f"Failed to execute command ({line}): {e}")

        def print_redirect(self, *args, **kwargs):
            """Redirect print calls to the output log"""
            text = " ".join(map(str, args))
            self.print_ansi(text)

        def print_ansi(self, text: str) -> None:
            """Print text to the output log with ANSI color support"""
            try:
                output_log = self.query_one("#output", RichLog)
                # RichLog automatically handles ANSI escape sequences
                output_log.write(text, expand=True)
            except Exception:
                # Avoid logging here to prevent recursion
                pass

        def clear_console(self) -> None:
            """Clear the console output"""
            try:
                output_log = self.query_one("#output", RichLog)
                output_log.clear()
            except Exception:
                # Avoid logging here to prevent recursion
                pass

        def update_status(self, status: str) -> None:
            """Update the status display in the banner"""
            self.status_text = status
            try:
                status_widget = self.query_one("#status-text", Static)
                status_widget.update(status)
            except Exception:
                # Avoid logging here to prevent recursion
                pass

        def action_quit(self) -> None:
            """Quit the application"""
            if self.exitCallback:
                self.exitCallback()
            self.exit()

        def start(self) -> None:
            """Start the console application"""
            self.run()

else:
    class SplitConsole:
        """Fallback console when Textual is not available"""
        def __init__(self, *args, **kwargs):
            print("Warning: Textual is not installed. SplitConsole is disabled.")
            
        def start(self):
            print("Cannot start SplitConsole - Textual is not available")
            
        def print_ansi(self, text: str) -> None:
            print(text)
            
        def clear_console(self) -> None:
            pass
            
        def update_status(self, status: str) -> None:
            pass

# Example usage:
if __name__ == '__main__':
    class DummySession:
        def parseCommand(self, cmd):
            print(f"Executing command: {cmd}")
        
        def getCompletions(self, text):
            return ["help", "exit", "clear", "status"]
    
    console = SplitConsole(
        session=DummySession(),
        bannerText="Test Console v1.0",
        historyFile="~/.test-history"
    )
    
    console.start()
"""
Terminal Second Brain - Todo TUI Application
A modern terminal user interface for managing todos.
"""

from textual.app import App
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual import on
from api_client import SyncTodoAPIClient
from todo_list import TodoList
from add_todo_screen import AddTodoScreen
import sys


class ConnectionErrorScreen(Screen):
    """Screen shown when API connection fails."""
    
    BINDINGS = [
        ("r", "retry", "Retry Connection"),
        ("q", "quit", "Quit Application"),
    ]
    
    def __init__(self, error_message: str):
        super().__init__()
        self.error_message = error_message
    
    def compose(self):
        """Compose the error screen."""
        with Vertical(classes="error-screen"):
            yield Static("🚫 Connection Error", classes="error-header")
            yield Static(f"Failed to connect to the Todo API:\n{self.error_message}", classes="error-message")
            yield Static("Press 'r' to retry or 'q' to quit", classes="error-help")
    
    def action_retry(self):
        """Retry connection action."""
        self.app.pop_screen()
        self.app.check_connection()
    
    def action_quit(self):
        """Quit application action."""
        self.app.exit()


class TodoApp(App):
    """Main Todo TUI Application."""
    
    CSS = """
    .header {
        height: 3;
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
    }
    
    .button-bar {
        height: 3;
        dock: bottom;
        background: $surface;
    }
    
    .add-todo-form {
        width: 50;
        height: 15;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    
    .form-header {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .label {
        margin-top: 1;
        margin-bottom: 1;
        text-style: bold;
    }
    
    .button-row {
        height: 3;
        margin-top: 1;
    }
    
    .error-screen {
        align: center middle;
        width: 60;
        height: 20;
        border: solid $error;
        background: $surface;
        padding: 2;
    }
    
    .error-header {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 2;
    }
    
    .error-message {
        text-align: center;
        margin-bottom: 2;
    }
    
    .error-help {
        text-align: center;
        text-style: italic;
        color: $text-muted;
    }
    
    DataTable {
        height: 1fr;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    TITLE = "Terminal Second Brain - Todo Manager"
    SUB_TITLE = "Manage your todos from the terminal"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_todo", "Add Todo"),
        ("r", "refresh", "Refresh"),
        ("?", "help", "Help"),
    ]
    
    SCREENS = {
        "add_todo": AddTodoScreen,
    }
    
    def __init__(self):
        super().__init__()
        self.api_client = SyncTodoAPIClient()
        self.todo_list = None
    
    def compose(self):
        """Compose the main application."""
        yield Header()
        
        # Check connection first
        if not self.check_connection():
            return
        
        self.todo_list = TodoList(self.api_client)
        yield self.todo_list
        
        yield Footer()
    
    def check_connection(self) -> bool:
        """Check API connection and show error screen if needed."""
        try:
            if not self.api_client.health_check():
                self.push_screen(ConnectionErrorScreen(
                    "The Todo API server is not responding.\n"
                    "Please ensure the Spring Boot application is running on http://localhost:8080"
                ))
                return False
            return True
        except Exception as e:
            self.push_screen(ConnectionErrorScreen(str(e)))
            return False
    
    def on_mount(self):
        """Handle app mounting."""
        if not self.check_connection():
            return
        
        self.notify("Welcome to Terminal Second Brain!", severity="information")
    
    def action_add_todo(self):
        """Add todo action."""
        if hasattr(self, 'todo_list'):
            self.push_screen("add_todo", AddTodoScreen(self.api_client))
    
    def action_refresh(self):
        """Refresh todos action."""
        if hasattr(self, 'todo_list') and self.todo_list:
            self.todo_list.load_todos()
    
    def action_help(self):
        """Show help."""
        help_text = """
        Terminal Second Brain - Todo Manager
        
        Keyboard Shortcuts:
        • q - Quit application
        • a - Add new todo
        • r - Refresh todo list
        • ? - Show this help
        • Esc - Cancel/Go back
        
        Mouse/Selection:
        • Click on a todo to select it
        • Use "Mark Complete" button to complete selected todo
        • Use "Add Todo" button to create new todos
        
        Navigation:
        • Use arrow keys to navigate
        • Tab to cycle through controls
        • Enter to activate buttons
        """
        self.notify(help_text, severity="information", timeout=10)
    
    def on_unmount(self):
        """Clean up when app closes."""
        if self.api_client:
            self.api_client.close()


def main():
    """Main entry point."""
    try:
        app = TodoApp()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

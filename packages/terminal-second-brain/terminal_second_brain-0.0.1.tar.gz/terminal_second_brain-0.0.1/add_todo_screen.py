"""
Add Todo Screen - form for creating new todos.
"""

from textual.screen import Screen
from textual.widgets import Input, Button, Static
from textual.containers import Horizontal, Vertical, Center
from textual.validation import Length
from textual import on
from api_client import TodoRequest, SyncTodoAPIClient


class AddTodoScreen(Screen):
    """Screen for adding new todos."""
    
    BINDINGS = [
        ("escape", "dismiss", "Cancel"),
        ("ctrl+s", "save", "Save Todo"),
    ]
    
    def __init__(self, api_client: SyncTodoAPIClient):
        super().__init__()
        self.api_client = api_client
    
    def compose(self):
        """Compose the add todo screen."""
        with Center():
            with Vertical(classes="add-todo-form"):
                yield Static("➕ Add New Todo", classes="form-header")
                
                yield Static("Title:", classes="label")
                yield Input(
                    placeholder="Enter todo title...",
                    validators=[Length(minimum=1, maximum=200)],
                    id="title-input"
                )
                
                with Horizontal(classes="button-row"):
                    yield Button("Save", id="save-btn", variant="primary")
                    yield Button("Cancel", id="cancel-btn", variant="default")
    
    def on_mount(self):
        """Focus the title input when screen mounts."""
        self.query_one("#title-input", Input).focus()
    
    @on(Button.Pressed, "#save-btn")
    def on_save_pressed(self):
        """Handle save button press."""
        self.save_todo()
    
    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_pressed(self):
        """Handle cancel button press."""
        self.dismiss()
    
    @on(Input.Submitted, "#title-input")
    def on_title_submitted(self):
        """Handle enter key in title input."""
        self.save_todo()
    
    def save_todo(self):
        """Save the new todo."""
        title_input = self.query_one("#title-input", Input)
        title = title_input.value.strip()
        
        if not title:
            self.app.notify("Please enter a todo title", severity="warning")
            title_input.focus()
            return
        
        try:
            todo_request = TodoRequest(title=title, completed=False)
            new_todo = self.api_client.create_todo(todo_request)
            
            self.app.notify(f"Todo '{new_todo.title}' created successfully!", severity="success")
            
            # Add todo to the main list if possible
            main_screen = self.app.screen
            if hasattr(main_screen, 'todo_list'):
                main_screen.todo_list.add_todo_to_list(new_todo)
            
            self.dismiss()
            
        except Exception as e:
            self.app.notify(f"Error creating todo: {e}", severity="error")
    
    def action_save(self):
        """Save action for keybinding."""
        self.save_todo()
    
    def action_dismiss(self):
        """Dismiss action for keybinding."""
        self.dismiss()
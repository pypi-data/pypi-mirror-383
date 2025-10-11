"""
Todo List Widget - displays todos and handles interactions.
"""

from textual.widgets import DataTable, Static, Button
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual import on
from rich.text import Text
from typing import List, Optional
from api_client import TodoResponse, SyncTodoAPIClient


class TodoList(Vertical):
    """Widget for displaying and managing todos."""
    
    todos: reactive[List[TodoResponse]] = reactive([], recompute=False)
    
    def __init__(self, api_client: SyncTodoAPIClient):
        super().__init__()
        self.api_client = api_client
        self.selected_todo: Optional[TodoResponse] = None
    
    def compose(self):
        """Compose the todo list widget."""
        yield Static("📋 Todo List", classes="header")
        
        # Create data table for todos
        table = DataTable(id="todo-table")
        table.add_columns("Status", "ID", "Title")
        table.cursor_type = "row"
        table.zebra_stripes = True
        yield table
        
        # Action buttons
        with Horizontal(classes="button-bar"):
            yield Button("Refresh", id="refresh-btn", variant="primary")
            yield Button("Mark Complete", id="complete-btn", variant="success")
            yield Button("Add Todo", id="add-btn", variant="default")
    
    def on_mount(self):
        """Load todos when widget mounts."""
        self.load_todos()
    
    def load_todos(self):
        """Load todos from the API."""
        try:
            self.todos = self.api_client.get_all_todos()
            self.update_table()
        except Exception as e:
            self.app.notify(f"Error loading todos: {e}", severity="error")
    
    def update_table(self):
        """Update the data table with current todos."""
        table = self.query_one("#todo-table", DataTable)
        table.clear()
        
        for todo in self.todos:
            status_icon = "✅" if todo.completed else "⭕"
            status_text = "Done" if todo.completed else "Pending"
            
            table.add_row(
                f"{status_icon} {status_text}",
                str(todo.id),
                todo.title,
                key=str(todo.id)
            )
    
    @on(DataTable.RowSelected, "#todo-table")
    def on_row_selected(self, event: DataTable.RowSelected):
        """Handle row selection in the table."""
        if event.row_key:
            todo_id = int(event.row_key.value)
            self.selected_todo = next(
                (todo for todo in self.todos if todo.id == todo_id), 
                None
            )
            
            # Update button states
            complete_btn = self.query_one("#complete-btn", Button)
            if self.selected_todo and not self.selected_todo.completed:
                complete_btn.disabled = False
                complete_btn.label = "Mark Complete"
            else:
                complete_btn.disabled = True
                complete_btn.label = "Already Complete"
    
    @on(Button.Pressed, "#refresh-btn")
    def on_refresh_pressed(self):
        """Handle refresh button press."""
        self.load_todos()
        self.app.notify("Todos refreshed!", severity="information")
    
    @on(Button.Pressed, "#complete-btn")
    def on_complete_pressed(self):
        """Handle mark complete button press."""
        if not self.selected_todo or self.selected_todo.completed:
            return
        
        try:
            updated_todo = self.api_client.mark_completed(self.selected_todo.id)
            self.app.notify(f"Todo '{updated_todo.title}' marked as complete!", severity="success")
            self.load_todos()  # Reload to show updated status
        except Exception as e:
            self.app.notify(f"Error marking todo complete: {e}", severity="error")
    
    @on(Button.Pressed, "#add-btn")
    def on_add_pressed(self):
        """Handle add todo button press."""
        self.app.push_screen("add_todo")
    
    def add_todo_to_list(self, todo: TodoResponse):
        """Add a new todo to the list (called from add screen)."""
        self.todos = self.todos + [todo]
        self.update_table()
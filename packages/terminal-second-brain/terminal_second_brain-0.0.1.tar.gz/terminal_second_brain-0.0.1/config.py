"""
Configuration and utilities for the Todo TUI application.
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""
    
    # API Configuration
    API_BASE_URL = os.getenv("TODO_API_URL", "http://localhost:8080")
    API_TIMEOUT = 10.0
    
    # UI Configuration
    MAX_TITLE_LENGTH = 200
    REFRESH_INTERVAL = 30  # seconds
    
    # Application Info
    APP_NAME = "Terminal Second Brain"
    APP_VERSION = "1.0.0"
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the configuration directory."""
        config_dir = Path.home() / ".config" / "terminal-second-brain"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir


class Colors:
    """Color scheme for the application."""
    
    # Status colors
    COMPLETED = "green"
    PENDING = "yellow"
    ERROR = "red"
    SUCCESS = "bright_green"
    INFO = "blue"
    WARNING = "orange3"
    
    # UI colors
    PRIMARY = "dodger_blue1"
    SECONDARY = "grey70"
    ACCENT = "purple"
    BACKGROUND = "grey11"
    SURFACE = "grey15"


class Icons:
    """Icons used throughout the application."""
    
    # Status icons
    COMPLETED = "✅"
    PENDING = "⭕"
    LOADING = "⏳"
    ERROR = "❌"
    SUCCESS = "✨"
    WARNING = "⚠️"
    INFO = "ℹ️"
    
    # Action icons
    ADD = "➕"
    REFRESH = "🔄"
    DELETE = "🗑️"
    EDIT = "✏️"
    COMPLETE = "☑️"
    
    # App icons
    TODO_LIST = "📋"
    BRAIN = "🧠"
    TERMINAL = "💻"


# Help text content
HELP_TEXT = f"""
{Icons.BRAIN} {Config.APP_NAME} v{Config.APP_VERSION}

{Icons.TERMINAL} KEYBOARD SHORTCUTS:
• q / Ctrl+C  - Quit application
• a          - Add new todo
• r          - Refresh todo list
• ?          - Show this help
• Esc        - Cancel/Go back
• Ctrl+S     - Save (in forms)
• Tab        - Navigate between controls
• Enter      - Activate selected item

{Icons.TODO_LIST} MOUSE CONTROLS:
• Click on todo - Select todo item
• Double-click  - Mark todo as complete
• Right-click   - Context menu (future)

{Icons.SUCCESS} FEATURES:
• View all todos with status indicators
• Add new todos with validation
• Mark todos as completed
• Real-time API connectivity status
• Keyboard and mouse navigation
• Responsive terminal interface

{Icons.INFO} CONNECTION:
API URL: {Config.API_BASE_URL}
Ensure your Spring Boot backend is running!
"""

STATUS_MESSAGES = {
    "loading": f"{Icons.LOADING} Loading todos...",
    "no_todos": f"{Icons.INFO} No todos found. Add one to get started!",
    "connection_error": f"{Icons.ERROR} Cannot connect to API server",
    "api_error": f"{Icons.ERROR} API returned an error",
    "success_create": f"{Icons.SUCCESS} Todo created successfully!",
    "success_complete": f"{Icons.SUCCESS} Todo marked as complete!",
    "success_refresh": f"{Icons.SUCCESS} Todos refreshed!",
    "error_empty_title": f"{Icons.WARNING} Please enter a todo title",
    "error_create": f"{Icons.ERROR} Failed to create todo",
    "error_complete": f"{Icons.ERROR} Failed to mark todo as complete",
}
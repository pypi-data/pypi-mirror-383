#!/usr/bin/env python3
"""
Simple CLI client for testing the Todo API without TUI.
Useful for debugging and testing the API client.
"""

import sys
import argparse
from api_client import SyncTodoAPIClient, TodoRequest


def test_connection(client: SyncTodoAPIClient) -> bool:
    """Test API connection."""
    print("🔍 Testing API connection...")
    try:
        if client.health_check():
            print("✅ API connection successful!")
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def list_todos(client: SyncTodoAPIClient):
    """List all todos."""
    print("\n📋 Fetching todos...")
    try:
        todos = client.get_all_todos()
        if not todos:
            print("ℹ️  No todos found")
            return
        
        print(f"\n📝 Found {len(todos)} todo(s):")
        print("-" * 50)
        for todo in todos:
            status = "✅ Done" if todo.completed else "⭕ Pending"
            print(f"ID: {todo.id:2d} | {status:10s} | {todo.title}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error fetching todos: {e}")


def add_todo(client: SyncTodoAPIClient, title: str):
    """Add a new todo."""
    print(f"\n➕ Adding todo: '{title}'")
    try:
        request = TodoRequest(title=title, completed=False)
        todo = client.create_todo(request)
        print(f"✅ Created todo with ID: {todo.id}")
    except Exception as e:
        print(f"❌ Error creating todo: {e}")


def complete_todo(client: SyncTodoAPIClient, todo_id: int):
    """Mark a todo as completed."""
    print(f"\n☑️  Marking todo {todo_id} as completed...")
    try:
        todo = client.mark_completed(todo_id)
        print(f"✅ Todo '{todo.title}' marked as completed!")
    except Exception as e:
        print(f"❌ Error completing todo: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Todo CLI Client")
    parser.add_argument("--url", default="http://localhost:8080", 
                       help="API base URL (default: http://localhost:8080)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Connection test
    subparsers.add_parser("test", help="Test API connection")
    
    # List todos
    subparsers.add_parser("list", help="List all todos")
    
    # Add todo
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Todo title")
    
    # Complete todo
    complete_parser = subparsers.add_parser("complete", help="Mark todo as completed")
    complete_parser.add_argument("id", type=int, help="Todo ID")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Interactive mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize client
    client = SyncTodoAPIClient(args.url)
    
    try:
        if args.command == "test":
            test_connection(client)
        
        elif args.command == "list":
            if test_connection(client):
                list_todos(client)
        
        elif args.command == "add":
            if test_connection(client):
                add_todo(client, args.title)
        
        elif args.command == "complete":
            if test_connection(client):
                complete_todo(client, args.id)
        
        elif args.command == "interactive":
            interactive_mode(client)
    
    finally:
        client.close()


def interactive_mode(client: SyncTodoAPIClient):
    """Interactive CLI mode."""
    if not test_connection(client):
        return
    
    print("\n🧠 Terminal Second Brain - Interactive Mode")
    print("Commands: list, add <title>, complete <id>, quit")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            elif cmd == "list":
                list_todos(client)
            
            elif cmd == "add" and len(command) > 1:
                title = " ".join(command[1:])
                add_todo(client, title)
            
            elif cmd == "complete" and len(command) == 2:
                try:
                    todo_id = int(command[1])
                    complete_todo(client, todo_id)
                except ValueError:
                    print("❌ Invalid ID. Please provide a number.")
            
            elif cmd == "help":
                print("\nAvailable commands:")
                print("  list              - Show all todos")
                print("  add <title>       - Add new todo")
                print("  complete <id>     - Mark todo as completed")
                print("  quit              - Exit interactive mode")
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
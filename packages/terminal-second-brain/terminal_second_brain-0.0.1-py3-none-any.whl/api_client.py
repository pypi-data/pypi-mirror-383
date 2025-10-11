"""
API client for the Todo application backend.
Handles all HTTP requests to the Spring Boot REST API.
"""

from __future__ import annotations

import httpx
from typing import List, Optional
from pydantic import BaseModel


class TodoRequest(BaseModel):
    """Request model for creating/updating todos."""
    title: str
    completed: bool = False


class TodoResponse(BaseModel):
    """Response model for todo data."""
    id: int
    title: str
    completed: bool


class TodoAPIClient:
    """Client for communicating with the Todo REST API."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=10.0)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    async def get_all_todos(self) -> List[TodoResponse]:
        """Fetch all todos from the API."""
        try:
            response = self.client.get("/api/v1/todos")
            response.raise_for_status()
            data = response.json()
            return [TodoResponse(**todo) for todo in data]
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    async def create_todo(self, todo_request: TodoRequest) -> TodoResponse:
        """Create a new todo."""
        try:
            response = self.client.post(
                "/api/v1/todos",
                json=todo_request.model_dump()
            )
            response.raise_for_status()
            return TodoResponse(**response.json())
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    async def mark_completed(self, todo_id: int) -> TodoResponse:
        """Mark a todo as completed."""
        try:
            response = self.client.patch(f"/api/v1/todos/{todo_id}/complete")
            response.raise_for_status()
            return TodoResponse(**response.json())
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Todo with ID {todo_id} not found")
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    def health_check(self) -> bool:
        """Check if the API is reachable."""
        try:
            response = self.client.get("/actuator/health", timeout=2.0)
            return response.status_code == 200
        except:
            return False


# Synchronous wrapper for easier use in Textual
class SyncTodoAPIClient:
    """Synchronous wrapper around the async API client."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.client = TodoAPIClient(base_url)
    
    def close(self):
        self.client.close()
    
    def get_all_todos(self) -> List[TodoResponse]:
        """Fetch all todos from the API."""
        # Since we're using httpx.Client (sync), we can call directly
        try:
            response = self.client.client.get("/api/v1/todos")
            response.raise_for_status()
            data = response.json()
            return [TodoResponse(**todo) for todo in data]
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    def create_todo(self, todo_request: TodoRequest) -> TodoResponse:
        """Create a new todo."""
        try:
            response = self.client.client.post(
                "/api/v1/todos",
                json=todo_request.model_dump()
            )
            response.raise_for_status()
            return TodoResponse(**response.json())
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    def mark_completed(self, todo_id: int) -> TodoResponse:
        """Mark a todo as completed."""
        try:
            response = self.client.client.patch(f"/api/v1/todos/{todo_id}/complete")
            response.raise_for_status()
            return TodoResponse(**response.json())
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Todo with ID {todo_id} not found")
            raise RuntimeError(f"API returned error {e.response.status_code}: {e.response.text}")
    
    def health_check(self) -> bool:
        """Check if the API is reachable."""
        try:
            response = self.client.client.get("/actuator/health", timeout=2.0)
            return response.status_code == 200
        except:
            return False
from __future__ import annotations

from pydantic import BaseModel

class TodoRequest(BaseModel):
    title: str
    completed: bool = False

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool

# Test the models
if __name__ == "__main__":
    req = TodoRequest(title="Test todo")
    print("Request:", req.model_dump())
    
    resp = TodoResponse(id=1, title="Test todo", completed=False)
    print("Response:", resp.model_dump())
    
    print("✅ Pydantic models work correctly!")
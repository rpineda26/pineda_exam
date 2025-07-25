"""Task model definition."""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class Task:
    """Task model representing a task entity."""
    
    def __init__(self, title: str, description: str = "", due_date: Optional[str] = None,
                 priority: str = "Medium", status: str = "Pending", 
                 task_id: Optional[ObjectId] = None, created_at: Optional[datetime] = None):
        """
        Initialize a Task instance.
        
        Args:
            title: Task title (required)
            description: Task description
            due_date: Due date in YYYY-MM-DD format
            priority: Priority level (High, Medium, Low)
            status: Task status (Pending, In Progress, Completed)
            task_id: MongoDB ObjectId (auto-generated if None)
            created_at: Creation timestamp (auto-generated if None)
        """
        self.task_id = task_id or ObjectId()
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for MongoDB storage."""
        return {
            "_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Task instance from dictionary."""
        return cls(
            task_id=data.get("_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            created_at=data.get("created_at")
        )
    
    def __str__(self) -> str:
        """String representation of the task."""
        return f"Task(id={self.task_id}, title='{self.title}', status='{self.status}')"
    
    def display(self) -> str:
        """Formatted display string for CLI output."""
        return f"""
ID: {self.task_id}
Title: {self.title}
Description: {self.description}
Due Date: {self.due_date or 'Not set'}
Priority: {self.priority}
Status: {self.status}
Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}
{'-' * 50}"""